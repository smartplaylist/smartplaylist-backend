import React from "react";
import "./TrackKey.css";

const TrackKey = (props) => {
    const key = [
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

    return (
        <div className={"key key-" + props.trackKey}>{key[props.trackKey]}</div>
    );
};

export default TrackKey;
