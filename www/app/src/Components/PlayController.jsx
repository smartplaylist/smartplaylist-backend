import React, { useEffect, useState } from "react";
import "./PlayController.css";

const PlayController = (props) => {
    const [playing, setPlaying] = useState("PLAY");

    const handleClick = (e) => {
        setPlaying(playing === "PLAY" ? "STOP" : "PLAY");
        props.onPlayClick();
    };

    useEffect(() => {});

    return (
        <div className="play-controller" onClick={handleClick}>
            {playing}
        </div>
    );
};

export default PlayController;
