import React, { Component } from "react";
import chroma from "chroma-js";
import { default as ReactSelect, components } from "react-select";

const color = chroma("#018281");

const MultiValueLabel = (props) => {
  let { data } = props;
  const label = data.label;

  // Shorten the label text to a maximum of 7 characters
  const shortenedLabel =
    label.length > 7
      ? label.substring(0, 7).replace(/\s+$/, "") + "..."
      : label;

  data = { ...data, label: shortenedLabel };

  return (
    <components.MultiValueLabel
      {...props}
      data={data}
      children={shortenedLabel}
    />
  );
};

const joblistStyles = {
  multiValue: (styles, { data }) => {
    return {
      ...styles,
      backgroundColor: color.alpha(0.1).css(),
    };
  },
  multiValueLabel: (styles, { data }) => ({
    ...styles,
    color: color,
  }),
  multiValueRemove: (styles, { data }) => {
    return {
      ...styles,
      color: color,
      ":hover": {
        backgroundColor: color,
        color: "white",
      },
    };
  },
  menu: (styles) => ({
    ...styles,
    borderRadius: 0,
  }),
  control: (styles) => ({
    ...styles,
    borderRadius: 0,
    boxShadow: "inset -2px -2px 0px #FFFFFF, inset 2px 2px 0px #000000",
  }),
  option: (styles, { data, isDisabled, isFocused, isSelected }) => {
    return {
      ...styles,
      backgroundColor: isDisabled
        ? undefined
        : isSelected
        ? color
        : isFocused
        ? color.alpha(0.1).css()
        : undefined,
      color: isDisabled ? "#ccc" : isSelected ? "grey" : color,
      cursor: isDisabled ? "not-allowed" : "default",

      ":active": {
        ...styles[":active"],
        backgroundColor: !isDisabled
          ? isSelected
            ? color
            : color.alpha(0.3).css()
          : undefined,
      },
    };
  },
  dropdownIndicator: () => ({
    display: "flex",
    alignItems: "center",
    padding: 0,
    margin: "auto",
  }),
  indicatorSeparator: () => ({
    display: "inline-block",
    width: 2,
    height: 20,
    marginRight: 2,
    // borderRadius: "50%",
    backgroundColor: "rgba(0, 0, 0, 0.2)",
  }),
  menuList: (styles) => ({
    ...styles,
    maxHeight: 150,
    overflowY: "scroll",
  }),
};

const jobOptions = [
  {
    label: "Chest Farming",
    options: [
      {
        value: "-Open-Chests-in-",
        label: "Open chests",
      },
      {
        value: "-Fight-in-",
        label: "Fight",
      },
      {
        value: "-Upgrade_cards-in-",
        label: "Upgrade cards",
      },
      {
        value: "-Random-Decks-in-",
        label: "Random decks",
      },
    ],
  },
  {
    label: "Clan",
    options: [
      {
        value: "-Requesting-in-",
        label: "Random Requesting",
      },
      {
        value: "-War-Participation-in-",
        label: "War Participation",
      },
    ],
  },
  {
    label: "Collection",
    options: [
      {
        value: "-Card-Mastery-Collection-in-",
        label: "Card Mastery Collection",
      },
      {
        value: "-Level-Up-Reward-Collection-in-",
        label: "Level Up Reward Collection",
      },
      {
        value: "-Battlepass-Reward-Collection-in-",
        label: "Battlepass Reward Collection",
      },
      {
        value: "-Free-Offer-Collection-in-",
        label: "Free Offer Collection",
      },
    ],
  },
];
export default class JobDropDown extends Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedOptions: [],
    };
  }

  handleChange = (selectedOptions) => {
    this.setState({ selectedOptions });
    this.props.onChange(selectedOptions);
  };

  render() {
    return (
      <span>
        <ReactSelect
          options={jobOptions}
          isMulti
          closeMenuOnSelect={false}
          hideSelectedOptions={false}
          components={{
            MultiValueLabel,
          }}
          placeholder={"Choose a job..."}
          onChange={this.handleChange}
          allowSelectAll={true}
          value={this.state.selectedOptions}
          styles={joblistStyles}
          maxMenuHeight={200}
        />
      </span>
    );
  }
}
