import React from "react";

export default function PlanDiagram2D({ boards }) {
  return (
    <div className="plan" style={{ gap: "24px" }}>
      {boards.map((board, i) => (
        <div key={i} style={{ marginBottom: "20px" }}>
          <div className="bar-label" style={{ marginBottom: "8px" }}>
            Tablero {i + 1} · {board.board_width} x {board.board_height} · Uso: {board.utilization}%
          </div>
          <svg 
            viewBox={`0 0 ${board.board_width} ${board.board_height}`} 
            style={{ width: "100%", maxHeight: "400px", border: "2px solid var(--ink)", background: "#fff" }}
          >
            {board.rectangles.map((rect, j) => (
              <g key={j}>
                <rect 
                  x={rect.x} 
                  y={rect.y} 
                  width={rect.width} 
                  height={rect.height} 
                  fill="hsl(210, 60%, 85%)" 
                  stroke="var(--ink)" 
                  strokeWidth="1"
                  vectorEffect="non-scaling-stroke"
                />
                <text 
                  x={rect.x + rect.width / 2} 
                  y={rect.y + rect.height / 2} 
                  textAnchor="middle" 
                  dominantBaseline="middle" 
                  fontSize={Math.max(12, Math.min(rect.width, rect.height) * 0.2)}
                  fill="var(--ink)"
                >
                  {rect.width}x{rect.height}
                </text>
              </g>
            ))}
          </svg>
        </div>
      ))}
    </div>
  );
}