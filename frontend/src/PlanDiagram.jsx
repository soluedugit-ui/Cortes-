import React from "react";

const fmt = (n) => Number(n.toFixed(2)).toString();

// Un color por largo de pieza distinto, para leer el plan de un vistazo en el taller.
function colorFor(length, lengths) {
  const i = lengths.indexOf(length);
  const hue = (i * 47) % 360;
  return `hsl(${hue} 55% 78%)`;
}

export default function PlanDiagram({ bars }) {
  const lengths = [...new Set(bars.flatMap((b) => b.pieces))].sort((a, b) => b - a);

  return (
    <div className="plan">
      {bars.map((bar, i) => {
        const total = bar.stock_length;
        return (
          <div className="bar-row" key={i}>
            <div className="bar-label">
              Barra {i + 1} · {fmt(total)}
            </div>
            <div className="bar">
              {bar.pieces.map((p, j) => (
                <React.Fragment key={j}>
                  {j > 0 && bar.kerf_loss > 0 && (
                    <div
                      className="kerf"
                      style={{ width: `${(bar.kerf_loss / (bar.pieces.length - 1) / total) * 100}%` }}
                      title="Corte de sierra"
                    />
                  )}
                  <div
                    className="piece"
                    style={{
                      width: `${(p / total) * 100}%`,
                      background: colorFor(p, lengths),
                    }}
                    title={fmt(p)}
                  >
                    {fmt(p)}
                  </div>
                </React.Fragment>
              ))}
              {bar.leftover > 0.005 && (
                <div
                  className="leftover"
                  style={{ width: `${(bar.leftover / total) * 100}%` }}
                  title="Sobrante"
                >
                  {bar.leftover / total > 0.06 ? fmt(bar.leftover) : ""}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
