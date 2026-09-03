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
