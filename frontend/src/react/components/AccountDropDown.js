import React, { Component } from "react";
import chroma from "chroma-js";
import { default as ReactSelect } from "react-select";

const color = chroma("#018281");

const accountListStyles = {
  multiValue: (styles, { data }) => {
    return {
      ...styles,
      backgroundColor: chroma(color).alpha(0.1).css(),
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

const accountOptions = [
  { value: "1", label: "1" },
  { value: "2", label: "2" },
  { value: "3", label: "3" },
  { value: "4", label: "4" },
  { value: "5", label: "5" },
  { value: "6", label: "6" },
  { value: "7", label: "7" },
  { value: "8", label: "8" },
];
export default class AccountDropDown extends Component {
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
          options={accountOptions}
          closeMenuOnSelect={false}
          hideSelectedOptions={false}
          placeholder={"# of Accounts"}
          onChange={this.handleChange}
          allowSelectAll={true}
          value={this.state.selectedOptions}
          styles={accountListStyles}
          maxMenuHeight={200}
        />
      </span>
    );
  }
}
