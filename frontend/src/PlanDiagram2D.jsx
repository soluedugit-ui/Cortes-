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
            style={{ 
              width: "100%", 
              maxHeight: "450px", 
              border: "3px solid var(--muted)", /* Borde exterior gris de tu logo */
              background: "#fdfdfd" 
            }}
          >
            {board.rectangles.map((rect, j) => (
              <g key={j}>
                <rect 
                  x={rect.x} 
                  y={rect.y} 
                  width={rect.width} 
                  height={rect.height} 
                  fill="#fdeee8" /* Un naranja muy suavecito de fondo */
                  stroke="var(--accent)" /* El naranja fuerte de tu logo para las líneas de corte */
                  strokeWidth="2"
                  vectorEffect="non-scaling-stroke"
                />
                <text 
                  x={rect.x + rect.width / 2} 
                  y={rect.y + rect.height / 2} 
                  textAnchor="middle" 
                  dominantBaseline="middle" 
                  fontSize={Math.max(14, Math.min(rect.width, rect.height) * 0.2)}
                  fill="var(--ink)"
                  fontWeight="bold"
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