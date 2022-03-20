import React from "react";
import "./Stats.css";

const Stats = (props) => {
    return (
        <ul id="stats">
            <li>Results: {props.totalResults}</li>
            <li>Total tracks: {props.totalTracks}</li>
        </ul>
    );
};

export default Stats;
