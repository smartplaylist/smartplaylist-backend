import React from "react";
import "./TrackKey.css";

export default class TrackKey extends React.Component {
    constructor(props) {
        super(props);
        this.key = [
            "C",
            "C♯",
            "D",
            "D♯",
            "E",
            "F",
            "F♯",
            "G",
            "G♯",
            "A",
            "A♯",
            "B",
        ];
    }
    render() {
        return (
            <div className={"key key-" + this.props.trackKey}>
                {this.key[this.props.trackKey]}
            </div>
        );
    }
}
