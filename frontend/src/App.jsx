import React, {
    useState,
    useEffect,
    useRef
}
from "react";


import GomokuBoard
from "./GomokuBoard";


import {
    move,
    getBoard,
    reset,
    newGame,
    chat,
    exportGame,
    runSelfPlay,
    getMonitorStatus
}
from "./api";





function App(){


    // Ref for chat messages container
    const chatEndRef = useRef(null);



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


    // Auto scroll to bottom when new message arrives
    useEffect(() => {
        if (chatEndRef.current) {
            chatEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [chatMessages]);


    // New game settings
    const [showNewGame, setShowNewGame] = useState(false);
    const [selectedSize, setSelectedSize] = useState(15);
    const [selectedDifficulty, setSelectedDifficulty] = useState("medium");
    const [gameInfo, setGameInfo] = useState(null);

    // Self play training
    const [showTraining, setShowTraining] = useState(false);
    const [trainingGames, setTrainingGames] = useState(10);
    const [training, setTraining] = useState(false);
    const [trainingResults, setTrainingResults] = useState(null);

    // Monitor
    const [showMonitor, setShowMonitor] = useState(false);
    const [monitorData, setMonitorData] = useState(null);
    const [monitorInterval, setMonitorInterval] = useState(null);







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


    async function handleNewGame(){

        try{

            const res = await newGame(selectedSize, selectedDifficulty);
            setBoard(res.data.board);
            setWinner(null);
            setWinningLine([]);
            setLastMove(null);
            setMessage("");
            setAiInfo(null);
            setMoveCount(0);
            setChatMessages([]);
            setGameInfo({
                size: res.data.size,
                difficulty: res.data.difficulty,
                simulations: res.data.simulations
            });
            setShowNewGame(false);

        }catch(error){

            console.error("创建新游戏失败:", error);

        }

    }


    async function handleExport(){

        try{

            const res = await exportGame(-1, "json");
            const content = res.data.content;

            // 创建下载
            const blob = new Blob([content], { type: "application/json" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `gomoku-game-${Date.now()}.json`;
            a.click();
            URL.revokeObjectURL(url);

        }catch(error){

            console.error("导出失败:", error);

        }

    }


    async function handleSelfPlay(){

        setTraining(true);
        setTrainingResults(null);

        try{

            const res = await runSelfPlay(trainingGames, selectedSize, 300);
            setTrainingResults(res.data.results);

        }catch(error){

            console.error("训练失败:", error);

        }finally{

            setTraining(false);

        }

    }


    // Monitor functions
    const fetchMonitorData = async () => {
        try {
            const res = await getMonitorStatus();
            setMonitorData(res.data);
        } catch (error) {
            console.error("获取监控数据失败:", error);
        }
    };


    const startMonitor = () => {
        setShowMonitor(true);
        fetchMonitorData();
        const interval = setInterval(fetchMonitorData, 1000);
        setMonitorInterval(interval);
    };


    const stopMonitor = () => {
        setShowMonitor(false);
        if (monitorInterval) {
            clearInterval(monitorInterval);
            setMonitorInterval(null);
        }
        setMonitorData(null);
    };


    // Cleanup monitor on unmount
    useEffect(() => {
        return () => {
            if (monitorInterval) {
                clearInterval(monitorInterval);
            }
        };
    }, [monitorInterval]);









    return (

        <div style={{
            minHeight: "100vh",
            background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
            display: "flex",
            flexDirection: "column",
            fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
        }}>

            {/* Header */}
            <div style={{
                textAlign: "center",
                padding: "20px 0",
                color: "white"
            }}>
                <h1 style={{
                    margin: "0 0 8px 0",
                    fontSize: "32px",
                    fontWeight: "700",
                    textShadow: "2px 2px 4px rgba(0,0,0,0.5)",
                    letterSpacing: "3px"
                }}>
                    GOMOKU AGENT
                </h1>
                <p style={{
                    margin: 0,
                    fontSize: "14px",
                    opacity: 0.7,
                    letterSpacing: "1px"
                }}>
                    LangGraph + MCTS + LLM
                </p>
            </div>



            {/* Main Content - Centered */}
            <div style={{
                flex: 1,
                display: "flex",
                justifyContent: "center",
                alignItems: "flex-start",
                padding: "0 20px 20px",
                gap: "24px"
            }}>



                {/* Left Panel - Controls */}
                <div style={{
                    width: "200px",
                    display: "flex",
                    flexDirection: "column",
                    gap: "12px"
                }}>
                    {/* Action Buttons */}
                    <div style={{
                        background: "rgba(255,255,255,0.1)",
                        borderRadius: "12px",
                        padding: "16px",
                        backdropFilter: "blur(10px)"
                    }}>
                        <div style={{
                            fontSize: "12px",
                            color: "rgba(255,255,255,0.6)",
                            marginBottom: "12px",
                            textTransform: "uppercase",
                            letterSpacing: "1px"
                        }}>
                            Actions
                        </div>

                        <button
                            onClick={() => setShowNewGame(true)}
                            style={{
                                width: "100%",
                                padding: "10px",
                                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                                color: "white",
                                border: "none",
                                borderRadius: "8px",
                                fontSize: "13px",
                                fontWeight: "600",
                                cursor: "pointer",
                                marginBottom: "8px"
                            }}
                        >
                            New Game
                        </button>

                        <button
                            onClick={restart}
                            style={{
                                width: "100%",
                                padding: "10px",
                                background: "rgba(255,255,255,0.2)",
                                color: "white",
                                border: "none",
                                borderRadius: "8px",
                                fontSize: "13px",
                                fontWeight: "600",
                                cursor: "pointer",
                                marginBottom: "8px"
                            }}
                        >
                            Reset
                        </button>

                        <button
                            onClick={handleExport}
                            style={{
                                width: "100%",
                                padding: "10px",
                                background: "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)",
                                color: "white",
                                border: "none",
                                borderRadius: "8px",
                                fontSize: "13px",
                                fontWeight: "600",
                                cursor: "pointer",
                                marginBottom: "8px"
                            }}
                        >
                            Export
                        </button>

                        <button
                            onClick={() => setShowTraining(true)}
                            style={{
                                width: "100%",
                                padding: "10px",
                                background: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
                                color: "white",
                                border: "none",
                                borderRadius: "8px",
                                fontSize: "13px",
                                fontWeight: "600",
                                cursor: "pointer",
                                marginBottom: "8px"
                            }}
                        >
                            Training
                        </button>

                        <button
                            onClick={showMonitor ? stopMonitor : startMonitor}
                            style={{
                                width: "100%",
                                padding: "10px",
                                background: showMonitor
                                    ? "linear-gradient(135deg, #f44336, #e91e63)"
                                    : "linear-gradient(135deg, #00b09b, #96c93d)",
                                color: "white",
                                border: "none",
                                borderRadius: "8px",
                                fontSize: "13px",
                                fontWeight: "600",
                                cursor: "pointer"
                            }}
                        >
                            {showMonitor ? "Stop Monitor" : "Monitor"}
                        </button>
                    </div>

                    {/* Game Info */}
                    {gameInfo && (
                        <div style={{
                            background: "rgba(255,255,255,0.1)",
                            borderRadius: "12px",
                            padding: "16px",
                            backdropFilter: "blur(10px)"
                        }}>
                            <div style={{
                                fontSize: "12px",
                                color: "rgba(255,255,255,0.6)",
                                marginBottom: "8px",
                                textTransform: "uppercase",
                                letterSpacing: "1px"
                            }}>
                                Game Settings
                            </div>
                            <div style={{color: "white", fontSize: "13px"}}>
                                <div>Board: {gameInfo.size}x{gameInfo.size}</div>
                                <div>Difficulty: {gameInfo.difficulty}</div>
                            </div>
                        </div>
                    )}

                    {/* Legend */}
                    <div style={{
                        background: "rgba(255,255,255,0.1)",
                        borderRadius: "12px",
                        padding: "16px",
                        backdropFilter: "blur(10px)"
                    }}>
                        <div style={{
                            fontSize: "12px",
                            color: "rgba(255,255,255,0.6)",
                            marginBottom: "12px",
                            textTransform: "uppercase",
                            letterSpacing: "1px"
                        }}>
                            Legend
                        </div>
                        <div style={{display: "flex", alignItems: "center", marginBottom: "8px"}}>
                            <div style={{
                                width: "14px", height: "14px", borderRadius: "50%",
                                background: "radial-gradient(circle at 35% 35%, #555, #000)",
                                marginRight: "8px", border: "1px solid rgba(255,255,255,0.3)"
                            }}></div>
                            <span style={{color: "white", fontSize: "12px"}}>You (Black)</span>
                        </div>
                        <div style={{display: "flex", alignItems: "center", marginBottom: "8px"}}>
                            <div style={{
                                width: "14px", height: "14px", borderRadius: "50%",
                                background: "radial-gradient(circle at 35% 35%, #fff, #ddd)",
                                marginRight: "8px", border: "1px solid rgba(255,255,255,0.3)"
                            }}></div>
                            <span style={{color: "white", fontSize: "12px"}}>AI (White)</span>
                        </div>
                        <div style={{display: "flex", alignItems: "center"}}>
                            <div style={{
                                width: "14px", height: "14px", borderRadius: "50%",
                                background: "transparent",
                                marginRight: "8px",
                                border: "3px solid #FF4444"
                            }}></div>
                            <span style={{color: "white", fontSize: "12px"}}>Winning</span>
                        </div>
                    </div>
                </div>



                {/* Center - Board */}
                <div style={{
                    background: "rgba(255,255,255,0.95)",
                    borderRadius: "16px",
                    padding: "20px",
                    boxShadow: "0 20px 60px rgba(0,0,0,0.4)",
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



                {/* Right Panel - Status & Chat */}
                <div style={{
                    width: "280px",
                    display: "flex",
                    flexDirection: "column",
                    gap: "12px"
                }}>
                    {/* Game Status */}
                    <div style={{
                        background: "rgba(255,255,255,0.1)",
                        borderRadius: "12px",
                        padding: "16px",
                        backdropFilter: "blur(10px)"
                    }}>
                        <div style={{
                            fontSize: "12px",
                            color: "rgba(255,255,255,0.6)",
                            marginBottom: "12px",
                            textTransform: "uppercase",
                            letterSpacing: "1px"
                        }}>
                            Status
                        </div>

                        <div style={{
                            background: winner
                                ? (winner === 1 ? "linear-gradient(135deg, #FFD700, #FFA500)" : "linear-gradient(135deg, #FF6B6B, #FF4444)")
                                : thinking
                                    ? "linear-gradient(135deg, #4ECDC4, #44BD9E)"
                                    : "linear-gradient(135deg, #667eea, #764ba2)",
                            borderRadius: "8px",
                            padding: "16px",
                            textAlign: "center",
                            color: "white",
                            minHeight: "60px",
                            display: "flex",
                            flexDirection: "column",
                            justifyContent: "center"
                        }}>
                            <div style={{fontSize: "20px", fontWeight: "bold"}}>
                                {winner
                                    ? (winner === 1 ? "You Win!" : "AI Wins!")
                                    : thinking
                                        ? "Thinking..."
                                        : "Your Turn"
                                }
                            </div>
                            {message && !winner && (
                                <div style={{fontSize: "12px", opacity: 0.9, marginTop: "4px"}}>
                                    {message}
                                </div>
                            )}
                        </div>

                        <div style={{
                            display: "flex",
                            justifyContent: "space-around",
                            marginTop: "12px"
                        }}>
                            <div style={{textAlign: "center"}}>
                                <div style={{fontSize: "20px", fontWeight: "bold", color: "white"}}>
                                    {moveCount}
                                </div>
                                <div style={{fontSize: "11px", color: "rgba(255,255,255,0.6)"}}>Moves</div>
                            </div>
                            <div style={{textAlign: "center"}}>
                                <div style={{fontSize: "20px", fontWeight: "bold", color: "white"}}>
                                    300
                                </div>
                                <div style={{fontSize: "11px", color: "rgba(255,255,255,0.6)"}}>Sims</div>
                            </div>
                        </div>
                    </div>

                    {/* AI Info */}
                    {aiInfo && (
                        <div style={{
                            background: "rgba(255,255,255,0.1)",
                            borderRadius: "12px",
                            padding: "16px",
                            backdropFilter: "blur(10px)"
                        }}>
                            <div style={{
                                fontSize: "12px",
                                color: "rgba(255,255,255,0.6)",
                                marginBottom: "12px",
                                textTransform: "uppercase",
                                letterSpacing: "1px"
                            }}>
                                AI Decision
                            </div>
                            <div style={{fontSize: "13px", color: "white"}}>
                                <div style={{marginBottom: "6px"}}>
                                    <span style={{opacity: 0.6}}>Type: </span>
                                    <span style={{
                                        background: aiInfo.type === "mcts" ? "#4CAF50" : aiInfo.type === "win" ? "#FF9800" : "#2196F3",
                                        padding: "2px 8px",
                                        borderRadius: "4px",
                                        fontSize: "11px"
                                    }}>
                                        {aiInfo.type || "N/A"}
                                    </span>
                                </div>
                                {aiInfo.move && (
                                    <div>
                                        <span style={{opacity: 0.6}}>Position: </span>
                                        <span>({aiInfo.move.join(", ")})</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Chat */}
                    <div style={{
                        background: "rgba(255,255,255,0.1)",
                        borderRadius: "12px",
                        padding: "16px",
                        backdropFilter: "blur(10px)",
                        flex: 1,
                        display: "flex",
                        flexDirection: "column",
                        minHeight: "300px"
                    }}>
                        <div style={{
                            fontSize: "12px",
                            color: "rgba(255,255,255,0.6)",
                            marginBottom: "12px",
                            textTransform: "uppercase",
                            letterSpacing: "1px"
                        }}>
                            Chat with AI
                        </div>

                        {/* Messages */}
                        <div style={{
                            flex: 1,
                            overflowY: "auto",
                            marginBottom: "12px",
                            padding: "8px",
                            background: "rgba(0,0,0,0.2)",
                            borderRadius: "8px"
                        }}>
                            {chatMessages.length === 0 && (
                                <div style={{
                                    textAlign: "center",
                                    color: "rgba(255,255,255,0.4)",
                                    padding: "20px",
                                    fontSize: "12px"
                                }}>
                                    Ask me about my moves!
                                </div>
                            )}

                            {chatMessages.map((msg, idx) => (
                                <div key={idx} style={{
                                    marginBottom: "8px",
                                    display: "flex",
                                    justifyContent: msg.role === "user" ? "flex-end" : "flex-start"
                                }}>
                                    <div style={{
                                        maxWidth: "85%",
                                        padding: "8px 12px",
                                        borderRadius: msg.role === "user"
                                            ? "10px 10px 0 10px"
                                            : "10px 10px 10px 0",
                                        background: msg.role === "user"
                                            ? "linear-gradient(135deg, #667eea, #764ba2)"
                                            : "rgba(255,255,255,0.2)",
                                        color: "white",
                                        fontSize: "12px",
                                        whiteSpace: "pre-wrap"
                                    }}>
                                        {msg.content}
                                    </div>
                                </div>
                            ))}

                            {chatLoading && (
                                <div style={{textAlign: "left", marginBottom: "8px"}}>
                                    <div style={{
                                        display: "inline-block",
                                        padding: "8px 12px",
                                        borderRadius: "10px 10px 10px 0",
                                        background: "rgba(255,255,255,0.2)",
                                        color: "white",
                                        fontSize: "12px"
                                    }}>
                                        Thinking...
                                    </div>
                                </div>
                            )}

                            <div ref={chatEndRef} />
                        </div>

                        {/* Input */}
                        <div style={{display: "flex", gap: "8px"}}>
                            <input
                                type="text"
                                value={chatInput}
                                onChange={(e) => setChatInput(e.target.value)}
                                onKeyPress={(e) => e.key === "Enter" && sendChat()}
                                placeholder="Ask AI..."
                                style={{
                                    flex: 1,
                                    padding: "10px",
                                    borderRadius: "8px",
                                    border: "1px solid rgba(255,255,255,0.2)",
                                    background: "rgba(0,0,0,0.2)",
                                    color: "white",
                                    fontSize: "12px",
                                    outline: "none"
                                }}
                            />
                            <button
                                onClick={sendChat}
                                disabled={chatLoading || !chatInput.trim()}
                                style={{
                                    padding: "10px 14px",
                                    background: chatLoading || !chatInput.trim()
                                        ? "rgba(255,255,255,0.2)"
                                        : "linear-gradient(135deg, #667eea, #764ba2)",
                                    color: "white",
                                    border: "none",
                                    borderRadius: "8px",
                                    cursor: chatLoading || !chatInput.trim() ? "not-allowed" : "pointer",
                                    fontSize: "12px"
                                }}
                            >
                                Send
                            </button>
                        </div>
                    </div>
                </div>

            </div>


            {/* Training Modal */}
            {showTraining && (
                <div style={{
                    position: "fixed",
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: "rgba(0,0,0,0.5)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    zIndex: 1000
                }}>
                    <div style={{
                        background: "white",
                        borderRadius: "16px",
                        padding: "32px",
                        width: "450px",
                        boxShadow: "0 20px 60px rgba(0,0,0,0.3)"
                    }}>
                        <h2 style={{
                            margin: "0 0 24px 0",
                            fontSize: "24px",
                            color: "#333"
                        }}>
                            AI Self-Play Training
                        </h2>


                        {/* Number of Games */}
                        <div style={{marginBottom: "20px"}}>
                            <label style={{
                                display: "block",
                                marginBottom: "8px",
                                fontWeight: "600",
                                color: "#555"
                            }}>
                                Number of Games
                            </label>
                            <div style={{display: "flex", gap: "10px"}}>
                                {[5, 10, 20, 50].map(num => (
                                    <button
                                        key={num}
                                        onClick={() => setTrainingGames(num)}
                                        style={{
                                            flex: 1,
                                            padding: "12px",
                                            background: trainingGames === num
                                                ? "linear-gradient(135deg, #f093fb, #f5576c)"
                                                : "#f0f0f0",
                                            color: trainingGames === num ? "white" : "#333",
                                            border: "none",
                                            borderRadius: "8px",
                                            cursor: "pointer",
                                            fontSize: "14px",
                                            fontWeight: "600"
                                        }}
                                    >
                                        {num}
                                    </button>
                                ))}
                            </div>
                        </div>


                        {/* Training Status */}
                        {training && (
                            <div style={{
                                marginBottom: "20px",
                                padding: "16px",
                                background: "#fff3e0",
                                borderRadius: "8px",
                                textAlign: "center"
                            }}>
                                <div style={{
                                    fontSize: "16px",
                                    fontWeight: "600",
                                    color: "#e65100"
                                }}>
                                    Training in progress...
                                </div>
                                <div style={{
                                    fontSize: "14px",
                                    color: "#bf360c",
                                    marginTop: "8px"
                                }}>
                                    Playing {trainingGames} games
                                </div>
                            </div>
                        )}


                        {/* Training Results */}
                        {trainingResults && !training && (
                            <div style={{
                                marginBottom: "20px",
                                padding: "16px",
                                background: "#e8f5e9",
                                borderRadius: "8px"
                            }}>
                                <div style={{
                                    fontSize: "16px",
                                    fontWeight: "600",
                                    color: "#2e7d32",
                                    marginBottom: "12px"
                                }}>
                                    Training Complete!
                                </div>

                                <div style={{display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px"}}>
                                    <div>
                                        <span style={{color: "#666"}}>Black Wins: </span>
                                        <span style={{fontWeight: "600"}}>{trainingResults.black_wins}</span>
                                    </div>
                                    <div>
                                        <span style={{color: "#666"}}>White Wins: </span>
                                        <span style={{fontWeight: "600"}}>{trainingResults.white_wins}</span>
                                    </div>
                                    <div>
                                        <span style={{color: "#666"}}>Draws: </span>
                                        <span style={{fontWeight: "600"}}>{trainingResults.draws}</span>
                                    </div>
                                    <div>
                                        <span style={{color: "#666"}}>Avg Moves: </span>
                                        <span style={{fontWeight: "600"}}>
                                            {trainingResults.total_moves / trainingGames}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        )}


                        {/* Buttons */}
                        <div style={{display: "flex", gap: "12px"}}>
                            <button
                                onClick={() => {
                                    setShowTraining(false);
                                    setTrainingResults(null);
                                }}
                                style={{
                                    flex: 1,
                                    padding: "14px",
                                    background: "#f0f0f0",
                                    color: "#333",
                                    border: "none",
                                    borderRadius: "8px",
                                    cursor: "pointer",
                                    fontSize: "16px",
                                    fontWeight: "600"
                                }}
                            >
                                Close
                            </button>
                            <button
                                onClick={handleSelfPlay}
                                disabled={training}
                                style={{
                                    flex: 1,
                                    padding: "14px",
                                    background: training
                                        ? "#ccc"
                                        : "linear-gradient(135deg, #f093fb, #f5576c)",
                                    color: "white",
                                    border: "none",
                                    borderRadius: "8px",
                                    cursor: training ? "not-allowed" : "pointer",
                                    fontSize: "16px",
                                    fontWeight: "600"
                                }}
                            >
                                {training ? "Training..." : "Start Training"}
                            </button>
                        </div>

                    </div>
                </div>
            )}


            {/* New Game Modal */}
            {showNewGame && (
                <div style={{
                    position: "fixed",
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: "rgba(0,0,0,0.5)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    zIndex: 1000
                }}>
                    <div style={{
                        background: "white",
                        borderRadius: "16px",
                        padding: "32px",
                        width: "400px",
                        boxShadow: "0 20px 60px rgba(0,0,0,0.3)"
                    }}>
                        <h2 style={{
                            margin: "0 0 24px 0",
                            fontSize: "24px",
                            color: "#333"
                        }}>
                            New Game Settings
                        </h2>


                        {/* Board Size */}
                        <div style={{marginBottom: "20px"}}>
                            <label style={{
                                display: "block",
                                marginBottom: "8px",
                                fontWeight: "600",
                                color: "#555"
                            }}>
                                Board Size
                            </label>
                            <div style={{display: "flex", gap: "10px"}}>
                                {[9, 13, 15].map(size => (
                                    <button
                                        key={size}
                                        onClick={() => setSelectedSize(size)}
                                        style={{
                                            flex: 1,
                                            padding: "12px",
                                            background: selectedSize === size
                                                ? "linear-gradient(135deg, #667eea, #764ba2)"
                                                : "#f0f0f0",
                                            color: selectedSize === size ? "white" : "#333",
                                            border: "none",
                                            borderRadius: "8px",
                                            cursor: "pointer",
                                            fontSize: "14px",
                                            fontWeight: "600"
                                        }}
                                    >
                                        {size}x{size}
                                    </button>
                                ))}
                            </div>
                        </div>


                        {/* Difficulty */}
                        <div style={{marginBottom: "24px"}}>
                            <label style={{
                                display: "block",
                                marginBottom: "8px",
                                fontWeight: "600",
                                color: "#555"
                            }}>
                                Difficulty
                            </label>
                            <div style={{display: "flex", gap: "10px"}}>
                                {["easy", "medium", "hard"].map(diff => (
                                    <button
                                        key={diff}
                                        onClick={() => setSelectedDifficulty(diff)}
                                        style={{
                                            flex: 1,
                                            padding: "12px",
                                            background: selectedDifficulty === diff
                                                ? diff === "easy"
                                                    ? "linear-gradient(135deg, #11998e, #38ef7d)"
                                                    : diff === "medium"
                                                        ? "linear-gradient(135deg, #667eea, #764ba2)"
                                                        : "linear-gradient(135deg, #eb3349, #f45c43)"
                                                : "#f0f0f0",
                                            color: selectedDifficulty === diff ? "white" : "#333",
                                            border: "none",
                                            borderRadius: "8px",
                                            cursor: "pointer",
                                            fontSize: "14px",
                                            fontWeight: "600",
                                            textTransform: "capitalize"
                                        }}
                                    >
                                        {diff}
                                    </button>
                                ))}
                            </div>
                        </div>


                        {/* Buttons */}
                        <div style={{display: "flex", gap: "12px"}}>
                            <button
                                onClick={() => setShowNewGame(false)}
                                style={{
                                    flex: 1,
                                    padding: "14px",
                                    background: "#f0f0f0",
                                    color: "#333",
                                    border: "none",
                                    borderRadius: "8px",
                                    cursor: "pointer",
                                    fontSize: "16px",
                                    fontWeight: "600"
                                }}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleNewGame}
                                style={{
                                    flex: 1,
                                    padding: "14px",
                                    background: "linear-gradient(135deg, #667eea, #764ba2)",
                                    color: "white",
                                    border: "none",
                                    borderRadius: "8px",
                                    cursor: "pointer",
                                    fontSize: "16px",
                                    fontWeight: "600"
                                }}
                            >
                                Start Game
                            </button>
                        </div>

                    </div>
                </div>
            )}

        </div>


    );



}



export default App;
