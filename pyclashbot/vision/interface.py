"""Pluggable interface for fight vision inference providers."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import numpy as np
from dataclasses import dataclass


@dataclass
class InferenceResult:
    """Standardized inference result structure."""
    units: List[Dict[str, Any]]
    hand_cards: List[Dict[str, Any]]
    tower_health: Dict[str, Dict[str, Any]]
    elapsed_ms: float


class InferenceProvider(ABC):
    """Abstract base class for inference providers."""
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the inference provider. Returns True if successful."""
        pass
    
    @abstractmethod
    def run_inference(self, image_bgr: np.ndarray, raw_image_bgr: Optional[np.ndarray] = None) -> InferenceResult:
        """
        Run inference on the provided image(s).
        
        Args:
            image_bgr: Preprocessed fight image (640x640) for unit detection
            raw_image_bgr: Raw image (633x419) for hand card extraction (optional)
            
        Returns:
            InferenceResult with detected units, hand cards, and tower health
        """
        pass
    
    @abstractmethod
    def cleanup(self):
        """Clean up resources."""
        pass


class LocalInferenceProvider(InferenceProvider):
    """Local ONNX-based inference provider."""
    
    def __init__(self, models_dir: str = None):
        """
        Initialize local inference provider.
        
        Args:
            models_dir: Path to directory containing ONNX models. If None, uses default.
        """
        from pathlib import Path
        
        if models_dir is None:
            models_dir = str(Path(__file__).parent.parent / "models")
        
        self.models_dir = Path(models_dir)
        self.vision_system = None
    
    def initialize(self) -> bool:
        """Initialize the local inference models."""
        try:
            from .inference import FightVision
            from .tracking.tracking_engine import TrackingEngine
            
            # Set up model paths
            det_model = str(self.models_dir / "detect-units.onnx")
            cls_model = str(self.models_dir / "classify-unit.onnx")
            side_model = str(self.models_dir / "classify-unit-side.onnx")
            hand_card_model = str(self.models_dir / "classify-hand-card.onnx")
            card_labels = str(self.models_dir / "card_class_to_idx.json")
            tower_cls_model = str(self.models_dir / "tower_health_inference_classification.onnx")
            tower_reg_model = str(self.models_dir / "tower_health_inference_regression.onnx")
            
            # Initialize the vision system
            self.vision_system = FightVision(
                det_model=det_model,
                cls_model=cls_model,
                side_classifier_model=side_model,
                hand_card_model=hand_card_model,
                hand_card_labels=card_labels,
                tower_health_classification_model=tower_cls_model,
                tower_health_regression_model=tower_reg_model,
                enable_tracking=True,
                save_crops=False,  # Disable crop saving for production
            )
            
            # Initialize tracking engine
            self.tracking_engine = TrackingEngine()
            
            return True
            
        except Exception as e:
            print(f"Failed to initialize local inference provider: {e}")
            return False
    
    def run_inference(self, image_bgr: np.ndarray, raw_image_bgr: Optional[np.ndarray] = None) -> InferenceResult:
        """Run local ONNX inference."""
        if self.vision_system is None:
            raise RuntimeError("Inference provider not initialized")
        
        import time
        start_time = time.perf_counter()
        
        # Run vision system inference
        raw_results = self.vision_system.run(image_bgr, raw_image_bgr)
        
        # Apply tracking/smoothing
        tracked_results = self.tracking_engine.update(raw_results)
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        return InferenceResult(
            units=tracked_results.get("units", []),
            hand_cards=tracked_results.get("hand_cards", []),
            tower_health=tracked_results.get("tower_health", {}),
            elapsed_ms=elapsed_ms
        )
    
    def cleanup(self):
        """Clean up local inference resources."""
        self.vision_system = None
        self.tracking_engine = None


class CloudInferenceProvider(InferenceProvider):
    """Cloud-based inference provider (placeholder for future implementation)."""
    
    def __init__(self, endpoint_url: str, api_key: str = None):
        """
        Initialize cloud inference provider.
        
        Args:
            endpoint_url: URL of the cloud inference endpoint
            api_key: Optional API key for authentication
        """
        self.endpoint_url = endpoint_url
        self.api_key = api_key
    
    def initialize(self) -> bool:
        """Initialize connection to cloud inference service."""
        # TODO: Implement cloud service initialization
        print("Cloud inference provider not yet implemented")
        return False
    
    def run_inference(self, image_bgr: np.ndarray, raw_image_bgr: Optional[np.ndarray] = None) -> InferenceResult:
        """Run cloud-based inference."""
        # TODO: Implement cloud inference
        raise NotImplementedError("Cloud inference not yet implemented")
    
    def cleanup(self):
        """Clean up cloud inference resources."""
        pass


class InferenceManager:
    """Manager for inference providers with fallback support."""
    
    def __init__(self, primary_provider: InferenceProvider, fallback_provider: InferenceProvider = None):
        """
        Initialize inference manager.
        
        Args:
            primary_provider: Primary inference provider to use
            fallback_provider: Optional fallback provider if primary fails
        """
        self.primary_provider = primary_provider
        self.fallback_provider = fallback_provider
        self.current_provider = None
    
    def initialize(self) -> bool:
        """Initialize the inference manager."""
        # Try primary provider first
        if self.primary_provider.initialize():
            self.current_provider = self.primary_provider
            return True
        
        # Try fallback if primary fails
        if self.fallback_provider and self.fallback_provider.initialize():
            print("Primary provider failed, using fallback")
            self.current_provider = self.fallback_provider
            return True
        
        return False
    
    def run_inference(self, image_bgr: np.ndarray, raw_image_bgr: Optional[np.ndarray] = None) -> InferenceResult:
        """Run inference using the current provider."""
        if self.current_provider is None:
            raise RuntimeError("No inference provider available")
        
        try:
            return self.current_provider.run_inference(image_bgr, raw_image_bgr)
        except Exception as e:
            # Try fallback if current provider fails
            if (self.current_provider == self.primary_provider and 
                self.fallback_provider and 
                self.fallback_provider != self.primary_provider):
                
                print(f"Primary provider failed ({e}), trying fallback")
                if self.fallback_provider.initialize():
                    self.current_provider = self.fallback_provider
                    return self.current_provider.run_inference(image_bgr, raw_image_bgr)
            
            raise
    
    def cleanup(self):
        """Clean up all providers."""
        if self.primary_provider:
            self.primary_provider.cleanup()
        if self.fallback_provider:
            self.fallback_provider.cleanup()
        self.current_provider = None