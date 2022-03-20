import React from "react";
import ReactPlayer from "react-player/lazy";
import "./Player.css";

const Player = (props) => {
    return (
        <div id="player">
            <ReactPlayer
                url={props.previewUrl}
                width={"100%"}
                height={"40px"}
                playing={true}
                controls={true}
                volume={0.05}
            />
        </div>
    );
};

export default Player;
