import React, { useState } from "react";

const MinMaxFilter = (props) => {
    const [showColumn, setShowColumn] = useState(props.showColumn);

    return (
        <div id={"min-max-filter-" + props.name} className="filter">
            <span className="label">{props.label}</span>
            <label htmlFor={"min" + props.label}>min</label>
            <input
                type="number"
                id={"min" + props.name}
                name={"min" + props.name}
                onChange={props.handler}
                defaultValue={props.minValue}
            />
            <label htmlFor={"max" + props.label}>max</label>
            <input
                type="number"
                id={"max" + props.name}
                name={"max" + props.name}
                onChange={props.handler}
                // TODO: This component does not take its value from state
                // because there is no `value` because I had trouble linking it
                // to the state. `value={props.minValue}` did not work
                // and was freezing the value (I guess because map() is making
                // a copy of an array with values. Using `defaultValue` works,
                // but when maxValue state is changed in other place, the change
                // will not be reflected in this field.
                defaultValue={props.maxValue}
            />
            <label htmlFor={"showColumn" + props.name}>Show column</label>
            <input
                type="checkbox"
                id={"showColumn" + props.name}
                name={"showColumn" + props.name}
                onChange={(e) => {
                    // TODO: why do I need to assign that?
                    // How do I get rid of that?
                    // Probably because the generic function "hander" uses "value" to set
                    // state in App component
                    e.target.value = e.target.checked;
                    setShowColumn(!showColumn);
                    props.handler(e);
                }}
                defaultChecked={showColumn}
            />
        </div>
    );
};

export default MinMaxFilter;
