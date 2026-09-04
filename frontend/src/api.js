import axios from "axios";


const API = axios.create({

    baseURL:
    import.meta.env.VITE_API_URL || "http://localhost:8000"

});



export function move(x,y){


    return API.post(
        "/move",
        {
            x,
            y
        }
    );


}



export function getBoard(){


    return API.get(
        "/board"
    );


}



export function reset(){


    return API.post(
        "/reset"
    );

}


export function newGame(size = 15, difficulty = "medium"){

    return API.post(
        "/new-game",
        {
            size,
            difficulty
        }
    );

}


export function chat(message){


    return API.post(
        "/chat",
        {
            message
        }
    );

}



export function getMemory(){


    return API.get(
        "/memory"
    );

}


export function exportGame(index = -1, format = "json"){

    return API.get(
        `/export/game/${index}?format=${format}`
    );

}


export function exportAllGames(format = "json"){

    return API.get(
        `/export/all?format=${format}`
    );

}


export function getGameSizes(){

    return API.get(
        "/game-sizes"
    );

}


export function getDifficulties(){

    return API.get(
        "/difficulties"
    );

}
