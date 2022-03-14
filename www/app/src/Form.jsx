import React from "react";

const serializeFormsInputs = () => {
    const form = document.getElementById("form");
    var params = [];
    for (var i = 0; i < form.elements.length; i++) {
        var field = form.elements[i];
        // Is there a const list of HTML elements
        // to be used here, maybe browser sensitive?
        if ("INPUT" === field.tagName) {
            params[field.name] = field.value;
        }
    }
    return params;
};

const Form = (props) => (
    <form className="pure-form" id="form">
        <fieldset>
            <legend>Search for tracks</legend>
            <label htmlFor="input">Artist or title</label>
            <input
                type="text"
                id="query"
                name="query"
                onChange={() => props.handler(serializeFormsInputs())}
                label="Search track"
            />
            <label htmlFor="released">Released</label>
            <input
                type="date"
                id="released"
                name="released"
                onChange={() => props.handler(serializeFormsInputs())}
                label="Released"
            />
            <label htmlFor="min-bpm">Min. BPM</label>
            <input
                type="number"
                id="min-bpm"
                name="min-bpm"
                onChange={() => props.handler(serializeFormsInputs())}
                label="Min. BPM s"
            />
            <label htmlFor="max-bpm">Max. BPM</label>
            <input
                type="number"
                id="max-bpm"
                name="max-bpm"
                onChange={() => props.handler(serializeFormsInputs())}
                label="Max. BPM s"
            />
            <label htmlFor="genre">Genre</label>
            <input
                type="text"
                id="genre"
                name="genre"
                onChange={() => props.handler(serializeFormsInputs())}
                label="Genre"
            />
            <label htmlFor="explicit">
                <input
                    type="checkbox"
                    id="explicit"
                    name="explicit"
                    onChange={() => props.handler(serializeFormsInputs())}
                    label="Explicit"
                />
                Explicit
            </label>
            <button
                type="submit"
                name="submit"
                className="pure-button pure-button-primary"
            >
                Search
            </button>
        </fieldset>
    </form>
);

export default Form;
