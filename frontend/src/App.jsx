import React, {
    useState,
    useEffect
}
from "react";


import GomokuBoard
from "./GomokuBoard";


import {
    move,
    getBoard,
    reset,
    chat
}
from "./api";





function App(){



    const empty =

    Array.from(

        {
            length:15
        },

        ()=>Array(15).fill(0)

    );




    const [board,setBoard] = useState(empty);


    const [message,setMessage] = useState("");


    const [thinking,setThinking] = useState(false);


    const [winner,setWinner] = useState(null);


    const [winningLine,setWinningLine] = useState([]);


    const [lastMove,setLastMove] = useState(null);


    const [aiInfo,setAiInfo] = useState(null);


    const [moveCount,setMoveCount] = useState(0);


    // Chat state
    const [chatMessages, setChatMessages] = useState([]);
    const [chatInput, setChatInput] = useState("");
    const [chatLoading, setChatLoading] = useState(false);







    useEffect(()=>{


        getBoard()

        .then(res=>{


            setBoard(

                res.data.board

            );


        });



    },[]);








    async function play(x,y){



        // 防止AI思考时继续点击

        if(
            thinking ||
            winner
        ){

            return;

        }





        // 已经有棋子

        if(
            board[x][y]!==0
        ){

            return;

        }




        // 保存当前棋盘状态，用于失败回滚
        const previousBoard = board.map(row => [...row]);
        const previousLastMove = lastMove;


        // 立即显示玩家棋子
        const temp = board.map(row => [...row]);
        temp[x][y] = 1;

        setBoard(temp);
        setLastMove([x, y]);
        setThinking(true);
        setMessage("AI思考中...");
        setMoveCount(prev => prev + 1);




        try{


            const res = await move(x, y);




            console.log(

                "AI返回:",

                res.data

            );





            // 更新棋盘

            setBoard(

                res.data.board

            );





            // 胜利状态

            setWinner(

                res.data.winner

            );





            // 胜利连线

            setWinningLine(

                res.data.winning_line || []

            );





            // 最后一步

            setLastMove(

                res.data.last_move

            );



            setMoveCount(prev => prev + 1);


            if(

                typeof res.data.message === "string"

            ){


                setMessage(

                    res.data.message

                );


            }

            else{


                setMessage(

                    res.data.message?.message || ""

                );


            }





            // AI详细信息

            setAiInfo(

                res.data.message

            );



        }


        catch(error){


            console.error(

                error

            );


            // 回滚到之前的棋盘状态
            setBoard(previousBoard);
            setLastMove(previousLastMove);
            setMoveCount(prev => prev - 1);

            setMessage("AI错误，请重试");



        }



        finally{


            setThinking(false);


        }



    }










    function restart(){



        reset()

        .then(res=>{


            setBoard(

                res.data.board

            );


            setWinner(null);


            setWinningLine([]);


            setLastMove(null);


            setMessage("");


            setAiInfo(null);
            setMoveCount(0);
            setChatMessages([]);



        });


    }


    async function sendChat(){


        if(!chatInput.trim() || chatLoading) return;


        const userMessage = chatInput.trim();
        setChatInput("");
        setChatMessages(prev => [...prev, {role: "user", content: userMessage}]);
        setChatLoading(true);


        try{

            const res = await chat(userMessage);
            setChatMessages(prev => [...prev, {role: "ai", content: res.data.response}]);

        }catch(error){

            setChatMessages(prev => [...prev, {role: "ai", content: "抱歉，暂时无法回答"}]);

        }finally{

            setChatLoading(false);

        }

    }









    return (

        <div style={{
            minHeight: "100vh",
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            padding: "20px",
            fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
        }}>

            {/* Header */}
            <div style={{
                textAlign: "center",
                marginBottom: "24px",
                color: "white"
            }}>
                <h1 style={{
                    margin: "0 0 8px 0",
                    fontSize: "36px",
                    fontWeight: "700",
                    textShadow: "2px 2px 4px rgba(0,0,0,0.3)",
                    letterSpacing: "2px"
                }}>
                    Gomoku Agent
                </h1>
                <p style={{
                    margin: 0,
                    fontSize: "16px",
                    opacity: 0.9
                }}>
                    LangGraph + MCTS AI
                </p>
            </div>



            {/* Main Content */}
            <div style={{
                display: "flex",
                gap: "32px",
                alignItems: "flex-start",
                flexWrap: "wrap",
                justifyContent: "center"
            }}>



                {/* Board Container */}
                <div style={{
                    background: "rgba(255,255,255,0.95)",
                    borderRadius: "16px",
                    padding: "24px",
                    boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
                    backdropFilter: "blur(10px)"
                }}>
                    <GomokuBoard
                        board={board}
                        onMove={play}
                        disabled={thinking || winner}
                        winningLine={winningLine}
                        lastMove={lastMove}
                        winner={winner}
                    />
                </div>



                {/* Info Panel */}
                <div style={{
                    background: "rgba(255,255,255,0.95)",
                    borderRadius: "16px",
                    padding: "24px",
                    width: "280px",
                    boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
                    backdropFilter: "blur(10px)"
                }}>

                    {/* Game Status */}
                    <div style={{
                        background: winner
                            ? (winner === 1 ? "linear-gradient(135deg, #FFD700, #FFA500)" : "linear-gradient(135deg, #FF6B6B, #FF4444)")
                            : thinking
                                ? "linear-gradient(135deg, #4ECDC4, #44BD9E)"
                                : "linear-gradient(135deg, #667eea, #764ba2)",
                        borderRadius: "12px",
                        padding: "20px",
                        textAlign: "center",
                        marginBottom: "20px",
                        color: "white",
                        minHeight: "80px",
                        display: "flex",
                        flexDirection: "column",
                        justifyContent: "center"
                    }}>
                        <div style={{
                            fontSize: "24px",
                            fontWeight: "bold",
                            marginBottom: "8px"
                        }}>
                            {winner
                                ? (winner === 1 ? "You Win!" : "AI Wins!")
                                : thinking
                                    ? "Thinking..."
                                    : "Your Turn"
                            }
                        </div>
                        {message && !winner && (
                            <div style={{fontSize: "14px", opacity: 0.9}}>
                                {message}
                            </div>
                        )}
                    </div>



                    {/* Move Counter */}
                    <div style={{
                        display: "flex",
                        justifyContent: "space-around",
                        marginBottom: "20px",
                        padding: "12px",
                        background: "#f8f9fa",
                        borderRadius: "8px"
                    }}>
                        <div style={{textAlign: "center"}}>
                            <div style={{fontSize: "24px", fontWeight: "bold", color: "#333"}}>
                                {moveCount}
                            </div>
                            <div style={{fontSize: "12px", color: "#666"}}>Moves</div>
                        </div>
                        <div style={{textAlign: "center"}}>
                            <div style={{fontSize: "24px", fontWeight: "bold", color: "#333"}}>
                                300
                            </div>
                            <div style={{fontSize: "12px", color: "#666"}}>Simulations</div>
                        </div>
                    </div>



                    {/* AI Info */}
                    {aiInfo && (
                        <div style={{
                            background: "#f8f9fa",
                            borderRadius: "8px",
                            padding: "16px",
                            marginBottom: "20px"
                        }}>
                            <div style={{
                                fontSize: "14px",
                                fontWeight: "600",
                                color: "#333",
                                marginBottom: "12px",
                                borderBottom: "1px solid #e0e0e0",
                                paddingBottom: "8px"
                            }}>
                                AI Info
                            </div>
                            <div style={{fontSize: "13px", color: "#555"}}>
                                <div style={{marginBottom: "8px"}}>
                                    <span style={{color: "#888"}}>Type: </span>
                                    <span style={{
                                        background: aiInfo.type === "mcts" ? "#4CAF50" : aiInfo.type === "win" ? "#FF9800" : "#2196F3",
                                        color: "white",
                                        padding: "2px 8px",
                                        borderRadius: "4px",
                                        fontSize: "12px"
                                    }}>
                                        {aiInfo.type || "N/A"}
                                    </span>
                                </div>
                                {aiInfo.move && (
                                    <div style={{marginBottom: "8px"}}>
                                        <span style={{color: "#888"}}>Position: </span>
                                        <span style={{fontWeight: "500"}}>
                                            ({aiInfo.move.join(", ")})
                                        </span>
                                    </div>
                                )}
                                {aiInfo.simulations && (
                                    <div>
                                        <span style={{color: "#888"}}>Sims: </span>
                                        <span style={{fontWeight: "500"}}>
                                            {aiInfo.simulations}
                                        </span>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}



                    {/* Restart Button */}
                    <button
                        onClick={restart}
                        style={{
                            width: "100%",
                            padding: "14px",
                            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                            color: "white",
                            border: "none",
                            borderRadius: "8px",
                            fontSize: "16px",
                            fontWeight: "600",
                            cursor: "pointer",
                            transition: "transform 0.2s, box-shadow 0.2s",
                            boxShadow: "0 4px 15px rgba(102, 126, 234, 0.4)"
                        }}
                        onMouseOver={(e) => {
                            e.target.style.transform = "translateY(-2px)";
                            e.target.style.boxShadow = "0 6px 20px rgba(102, 126, 234, 0.6)";
                        }}
                        onMouseOut={(e) => {
                            e.target.style.transform = "translateY(0)";
                            e.target.style.boxShadow = "0 4px 15px rgba(102, 126, 234, 0.4)";
                        }}
                    >
                        New Game
                    </button>



                    {/* Legend */}
                    <div style={{
                        marginTop: "20px",
                        padding: "12px",
                        background: "#f8f9fa",
                        borderRadius: "8px",
                        fontSize: "12px",
                        color: "#666"
                    }}>
                        <div style={{marginBottom: "8px", fontWeight: "600", color: "#333"}}>Legend</div>
                        <div style={{display: "flex", alignItems: "center", marginBottom: "6px"}}>
                            <div style={{
                                width: "16px", height: "16px", borderRadius: "50%",
                                background: "black", marginRight: "8px", border: "1px solid #333"
                            }}></div>
                            <span>You (Black)</span>
                        </div>
                        <div style={{display: "flex", alignItems: "center", marginBottom: "6px"}}>
                            <div style={{
                                width: "16px", height: "16px", borderRadius: "50%",
                                background: "white", marginRight: "8px", border: "1px solid #999"
                            }}></div>
                            <span>AI (White)</span>
                        </div>
                        <div style={{display: "flex", alignItems: "center"}}>
                            <div style={{
                                width: "16px", height: "16px", borderRadius: "50%",
                                background: "transparent", marginRight: "8px",
                                border: "3px solid #FF4444"
                            }}></div>
                            <span>Winning Line</span>
                        </div>
                    </div>

                </div>


                {/* Chat Panel */}
                <div style={{
                    background: "rgba(255,255,255,0.95)",
                    borderRadius: "16px",
                    padding: "24px",
                    width: "320px",
                    boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
                    backdropFilter: "blur(10px)",
                    display: "flex",
                    flexDirection: "column",
                    height: "500px"
                }}>

                    {/* Chat Header */}
                    <div style={{
                        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                        borderRadius: "12px",
                        padding: "16px",
                        marginBottom: "16px",
                        color: "white"
                    }}>
                        <div style={{fontSize: "18px", fontWeight: "600"}}>
                            Chat with AI
                        </div>
                        <div style={{fontSize: "12px", opacity: 0.9, marginTop: "4px"}}>
                            Ask about AI's thinking
                        </div>
                    </div>


                    {/* Messages */}
                    <div style={{
                        flex: 1,
                        overflowY: "auto",
                        marginBottom: "12px",
                        padding: "8px",
                        background: "#f8f9fa",
                        borderRadius: "8px"
                    }}>
                        {chatMessages.length === 0 && (
                            <div style={{
                                textAlign: "center",
                                color: "#999",
                                padding: "20px",
                                fontSize: "14px"
                            }}>
                                Ask me anything about my moves!
                            </div>
                        )}

                        {chatMessages.map((msg, idx) => (
                            <div key={idx} style={{
                                marginBottom: "12px",
                                display: "flex",
                                justifyContent: msg.role === "user" ? "flex-end" : "flex-start"
                            }}>
                                <div style={{
                                    maxWidth: "80%",
                                    padding: "10px 14px",
                                    borderRadius: msg.role === "user"
                                        ? "12px 12px 0 12px"
                                        : "12px 12px 12px 0",
                                    background: msg.role === "user"
                                        ? "linear-gradient(135deg, #667eea, #764ba2)"
                                        : "white",
                                    color: msg.role === "user" ? "white" : "#333",
                                    fontSize: "14px",
                                    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                                    whiteSpace: "pre-wrap"
                                }}>
                                    {msg.content}
                                </div>
                            </div>
                        ))}

                        {chatLoading && (
                            <div style={{
                                textAlign: "left",
                                marginBottom: "12px"
                            }}>
                                <div style={{
                                    display: "inline-block",
                                    padding: "10px 14px",
                                    borderRadius: "12px 12px 12px 0",
                                    background: "white",
                                    boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
                                }}>
                                    <span style={{animation: "pulse 1s infinite"}}>Thinking...</span>
                                </div>
                            </div>
                        )}
                    </div>


                    {/* Input */}
                    <div style={{
                        display: "flex",
                        gap: "8px"
                    }}>
                        <input
                            type="text"
                            value={chatInput}
                            onChange={(e) => setChatInput(e.target.value)}
                            onKeyPress={(e) => e.key === "Enter" && sendChat()}
                            placeholder="Ask AI..."
                            style={{
                                flex: 1,
                                padding: "12px",
                                borderRadius: "8px",
                                border: "1px solid #ddd",
                                fontSize: "14px",
                                outline: "none"
                            }}
                        />
                        <button
                            onClick={sendChat}
                            disabled={chatLoading || !chatInput.trim()}
                            style={{
                                padding: "12px 16px",
                                background: chatLoading || !chatInput.trim()
                                    ? "#ccc"
                                    : "linear-gradient(135deg, #667eea, #764ba2)",
                                color: "white",
                                border: "none",
                                borderRadius: "8px",
                                cursor: chatLoading || !chatInput.trim() ? "not-allowed" : "pointer",
                                fontSize: "14px"
                            }}
                        >
                            Send
                        </button>
                    </div>

                </div>

            </div>

        </div>


    );



}



export default App;
