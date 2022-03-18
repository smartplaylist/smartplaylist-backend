import React from "react";

export default class MinMaxFilter extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            showColumn: this.props.showColumn,
        };
    }
    render() {
        return (
            <div id={"min-max-filter-" + this.props.name} className="filter">
                <span className="label">{this.props.label}</span>
                <label htmlFor={"min" + this.props.label}>min</label>
                <input
                    type="number"
                    id={"min" + this.props.name}
                    name={"min" + this.props.name}
                    onChange={this.props.handler}
                    defaultValue={this.props.minValue}
                />
                <label htmlFor={"max" + this.props.label}>max</label>
                <input
                    type="number"
                    id={"max" + this.props.name}
                    name={"max" + this.props.name}
                    onChange={this.props.handler}
                    // TODO: This component does not take its value from state
                    // because there is no `value` because I had trouble linking it
                    // to the state. `value={this.props.minValue}` did not work
                    // and was freezing the value (I guess because map() is making
                    // a copy of an array with values. Using `defaultValue` works,
                    // but when maxValue state is changed in other place, the change
                    // will not be reflected in this field.
                    defaultValue={this.props.maxValue}
                />
                <label htmlFor={"showColumn" + this.props.name}>
                    Show column
                </label>
                <input
                    type="checkbox"
                    id={"showColumn" + this.props.name}
                    name={"showColumn" + this.props.name}
                    // TODO: checked is different from value. Currently it's the opposite
                    onChange={(e) => {
                        e.target.value = this.state.showColumn;
                        this.setState({ showColumn: !this.state.showColumn });
                        this.props.handler(e);
                    }}
                    checked={this.state.showColumn}
                />
            </div>
        );
    }
}
