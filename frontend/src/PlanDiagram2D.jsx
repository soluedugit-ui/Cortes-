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
              maxHeight: "500px", 
              /* Eliminamos el borde engañoso de aquí */
            }}
          >
            {/* 1. EL VERDADERO TABLERO (Fondo gris claro con borde oscuro) */}
            <rect 
              x="0" 
              y="0" 
              width={board.board_width} 
              height={board.board_height} 
              fill="#f9fafb" 
              stroke="var(--muted)" 
              strokeWidth="4"
              vectorEffect="non-scaling-stroke"
            />

            {/* 2. LAS PIEZAS CORTADAS */}
            {board.rectangles.map((rect, j) => (
              <g key={j}>
                <rect 
                  x={rect.x} 
                  y={rect.y} 
                  width={rect.width} 
                  height={rect.height} 
                  fill="#fdeee8" 
                  stroke="var(--accent)" 
                  strokeWidth="2"
                  vectorEffect="non-scaling-stroke"
                />
                <text 
                  x={rect.x + rect.width / 2} 
                  y={rect.y + rect.height / 2} 
                  textAnchor="middle" 
                  dominantBaseline="middle" 
                  /* Esto asegura que el texto jamás se salga de las cajas, sin importar lo pequeñas que sean */
                  fontSize={Math.min(rect.width, rect.height) * 0.3}
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