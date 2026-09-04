import React from "react";



function GomokuBoard({

board,

onMove,

disabled,

winningLine,

lastMove,

winner

}){


// 动态计算棋盘大小
const size = board.length;
const cell = size <= 9 ? 50 : size <= 13 ? 44 : 40;
const padding = 20;
const boardSize = (size - 1) * cell + padding * 2;


// 星位坐标（根据棋盘大小动态计算）
const getStarPoints = (boardSize) => {
    if (boardSize === 9) {
        return [[2, 2], [2, 6], [4, 4], [6, 2], [6, 6]];
    } else if (boardSize === 13) {
        return [[3, 3], [3, 9], [6, 6], [9, 3], [9, 9]];
    } else {
        return [[3, 3], [3, 11], [7, 7], [11, 3], [11, 11]];
    }
};

const starPoints = getStarPoints(size);

function isStarPoint(x, y) {
    return starPoints.some(([sx, sy]) => sx === x && sy === y);
}


function click(e){


    if(disabled)

        return;




    const rect = e.currentTarget.getBoundingClientRect();



    const x = Math.round((e.clientY - rect.top - padding) / cell);
    const y = Math.round((e.clientX - rect.left - padding) / cell);



    if(x >= 0 && x < size && y >= 0 && y < size){

        onMove(x, y);

    }


}





function isWin(x, y){


    return winningLine.some(

        p => p[0] === x && p[1] === y

    );

}



return (

    <div style={{
        position: "relative",
        display: "inline-block"
    }}>

        {/* Board Container */}
        <div
            onClick={click}
            style={{
                width: boardSize,
                height: boardSize,
                background: "linear-gradient(145deg, #DEB887 0%, #D2A06D 50%, #C4944D 100%)",
                borderRadius: "4px",
                position: "relative",
                cursor: disabled ? "not-allowed" : "pointer",
                boxShadow: "inset 0 2px 10px rgba(0,0,0,0.2), 0 4px 20px rgba(0,0,0,0.3)"
            }}
        >


            {/* Grid Lines */}
            {[...Array(size)].map((_, i) => (
                <React.Fragment key={i}>

                    {/* Horizontal Line */}
                    <div style={{
                        position: "absolute",
                        top: i * cell + padding,
                        left: padding,
                        width: (size - 1) * cell,
                        height: 1,
                        background: "rgba(0,0,0,0.4)"
                    }}/>

                    {/* Vertical Line */}
                    <div style={{
                        position: "absolute",
                        left: i * cell + padding,
                        top: padding,
                        height: (size - 1) * cell,
                        width: 1,
                        background: "rgba(0,0,0,0.4)"
                    }}/>

                </React.Fragment>
            ))}


            {/* Star Points */}
            {starPoints.map(([x, y]) => (
                <div
                    key={`star-${x}-${y}`}
                    style={{
                        position: "absolute",
                        left: y * cell + padding - 5,
                        top: x * cell + padding - 5,
                        width: 10,
                        height: 10,
                        borderRadius: "50%",
                        background: "rgba(0,0,0,0.5)"
                    }}
                />
            ))}


            {/* Stones */}
            {board.map((row, x) =>
                row.map((v, y) => {
                    if(v === 0)
                        return null;

                    const isWinStone = isWin(x, y);
                    const isLast = lastMove && lastMove[0] === x && lastMove[1] === y;

                    return (
                        <div
                            key={`${x}-${y}`}
                            style={{
                                position: "absolute",
                                left: y * cell + padding - 17,
                                top: x * cell + padding - 17,
                                width: 34,
                                height: 34,
                                borderRadius: "50%",
                                background: v === 1
                                    ? "radial-gradient(circle at 35% 35%, #555, #000 60%, #111)"
                                    : "radial-gradient(circle at 35% 35%, #fff, #ddd 60%, #eee)",
                                border: isWinStone
                                    ? "3px solid #FF4444"
                                    : isLast
                                        ? "3px solid #2196F3"
                                        : v === 1
                                            ? "1px solid rgba(0,0,0,0.5)"
                                            : "1px solid rgba(200,200,200,0.8)",
                                boxShadow: isWinStone
                                    ? "0 0 15px rgba(255,68,68,0.6)"
                                    : isLast
                                        ? "0 0 10px rgba(33,150,243,0.5)"
                                        : v === 1
                                            ? "2px 2px 6px rgba(0,0,0,0.4)"
                                            : "2px 2px 6px rgba(0,0,0,0.2)",
                                pointerEvents: "none",
                                transition: "all 0.2s ease"
                            }}
                        />
                    );
                })
            )}


            {/* Last Move Indicator */}
            {lastMove && !winner && (
                <div style={{
                    position: "absolute",
                    left: lastMove[1] * cell + padding - 4,
                    top: lastMove[0] * cell + padding - 4,
                    width: 8,
                    height: 8,
                    borderRadius: "50%",
                    background: board[lastMove[0]][lastMove[1]] === 1 ? "#4CAF50" : "#FF5722",
                    pointerEvents: "none",
                    zIndex: 10
                }}/>
            )}


            {/* Coordinate Labels */}
            {[...Array(size)].map((_, i) => (
                <React.Fragment key={`label-${i}`}>

                    {/* Top labels (A-O) */}
                    <div style={{
                        position: "absolute",
                        left: i * cell + padding,
                        top: 2,
                        transform: "translateX(-50%)",
                        fontSize: "10px",
                        color: "rgba(0,0,0,0.4)",
                        fontFamily: "monospace"
                    }}>
                        {String.fromCharCode(65 + i)}
                    </div>

                    {/* Left labels (1-15) */}
                    <div style={{
                        position: "absolute",
                        top: i * cell + padding,
                        left: 2,
                        transform: "translateY(-50%)",
                        fontSize: "10px",
                        color: "rgba(0,0,0,0.4)",
                        fontFamily: "monospace"
                    }}>
                        {i + 1}
                    </div>

                </React.Fragment>
            ))}


            {/* Hover Effect Area */}
            {disabled && (
                <div style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: "rgba(0,0,0,0.1)",
                    borderRadius: "4px"
                }}/>
            )}

        </div>

    </div>


);


}



export default GomokuBoard;
