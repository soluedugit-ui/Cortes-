import React, { useState } from "react";
import { optimizeCuts, optimizeCuts2D } from "./api.js";
import PlanDiagram from "./PlanDiagram.jsx";
import PlanDiagram2D from "./PlanDiagram2D.jsx"; // Importamos el nuevo diagrama

const fmt = (n) => Number(n.toFixed(2)).toString();

function EditableTable({ title, rows, setRows, columns, newRow, hint }) {
  const update = (i, key, value) =>
    setRows(rows.map((r, idx) => (idx === i ? { ...r, [key]: value } : r)));
  return (
    <section className="card">
      <h2>{title}</h2>
      {hint && <p className="hint">{hint}</p>}
      <table>
        <thead>
          <tr>
            {columns.map((c) => (
              <th key={c.key}>{c.label}</th>
            ))}
            <th />
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              {columns.map((c) => (
                <td key={c.key}>
                  <input
                    type="number"
                    min="0"
                    step="any"
                    value={r[c.key]}
                    placeholder={c.placeholder}
                    onChange={(e) => update(i, c.key, e.target.value)}
                  />
                </td>
              ))}
              <td>
                <button
                  className="link"
                  onClick={() => setRows(rows.filter((_, idx) => idx !== i))}
                  aria-label="Quitar fila"
                >
                  ✕
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <button className="secondary" onClick={() => setRows([...rows, newRow()])}>
        + Agregar fila
      </button>
    </section>
  );
}

export default function App() {
  // Pestaña actual: "1D" o "2D"
  const [appMode, setAppMode] = useState("1D");

  // Estado 1D
  const [pieces1D, setPieces1D] = useState([
    { length: "1250", quantity: "8" },
    { length: "830", quantity: "10" },
    { length: "410", quantity: "14" },
  ]);
  const [stock1D, setStock1D] = useState([{ length: "6000", quantity: "" }]);
  const [method1D, setMethod1D] = useState("fast");

  // Estado 2D
  const [pieces2D, setPieces2D] = useState([
    { width: "800", height: "600", quantity: "4" },
    { width: "400", height: "400", quantity: "6" }
  ]);
  const [stock2D, setStock2D] = useState([{ width: "2440", height: "1220", quantity: "" }]);
  const [allowRotation, setAllowRotation] = useState(true);

  // Estados compartidos
  const [kerf, setKerf] = useState("3");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [slow, setSlow] = useState(false);

  const calculate = async () => {
    setError("");
    setResult(null);
    setSlow(false);
    setLoading(true);

    const slowTimer = setTimeout(() => setSlow(true), 4000);

    try {
      if (appMode === "1D") {
        const payload = {
          pieces: pieces1D
            .filter((p) => p.length && p.quantity)
            .map((p) => ({ length: Number(p.length), quantity: Number(p.quantity) })),
          stock: stock1D
            .filter((s) => s.length)
            .map((s) => ({
              length: Number(s.length),
              quantity: s.quantity === "" ? null : Number(s.quantity),
            })),
          kerf: Number(kerf || 0),
          mode: method1D,
        };
        if (!payload.pieces.length || !payload.stock.length) {
          throw new Error("Agrega al menos una pieza y una barra.");
        }
        const data = await optimizeCuts(payload);
        setResult({ type: "1D", data });
      } else {
        // Lógica 2D
        const payload = {
          pieces: pieces2D
            .filter((p) => p.width && p.height && p.quantity)
            .map((p) => ({ width: Number(p.width), height: Number(p.height), quantity: Number(p.quantity) })),
          stock: stock2D
            .filter((s) => s.width && s.height)
            .map((s) => ({
              width: Number(s.width),
              height: Number(s.height),
              quantity: s.quantity === "" ? null : Number(s.quantity),
            })),
          kerf: Number(kerf || 0),
          allow_rotation: allowRotation,
        };
        if (!payload.pieces.length || !payload.stock.length) {
          throw new Error("Agrega al menos una pieza y un tablero.");
        }
        const data = await optimizeCuts2D(payload);
        setResult({ type: "2D", data });
      }
    } catch (e) {
      setError(e.message);
    } finally {
      clearTimeout(slowTimer);
      setSlow(false);
      setLoading(false);
    }
  };

  return (
    <main>
      <header>
        <h1>Optimizador de cortes</h1>
        <p>Usa la misma unidad en todo (ej. mm, cm).</p>
        <div className="tabs">
          <button 
            className={appMode === "1D" ? "" : "secondary"} 
            onClick={() => { setAppMode("1D"); setResult(null); }}
          >
            Corte Lineal (1D)
          </button>
          <button 
            className={appMode === "2D" ? "" : "secondary"} 
            onClick={() => { setAppMode("2D"); setResult(null); }}
          >
            Tableros / Paneles (2D)
          </button>
        </div>
      </header>

      {appMode === "1D" ? (
        <div className="grid">
          <EditableTable
            title="Piezas a cortar (Tubos, Barras)"
            rows={pieces1D}
            setRows={setPieces1D}
            columns={[
              { key: "length", label: "Largo", placeholder: "1250" },
              { key: "quantity", label: "Cantidad", placeholder: "8" },
            ]}
            newRow={() => ({ length: "", quantity: "" })}
          />
          <EditableTable
            title="Barras disponibles"
            hint="Deja la cantidad vacía si tienes todas las que necesites."
            rows={stock1D}
            setRows={setStock1D}
            columns={[
              { key: "length", label: "Largo", placeholder: "6000" },
              { key: "quantity", label: "Cantidad (opcional)", placeholder: "∞" },
            ]}
            newRow={() => ({ length: "", quantity: "" })}
          />
        </div>
      ) : (
        <div className="grid">
          <EditableTable
            title="Piezas a cortar (Madera, Metal, etc.)"
            rows={pieces2D}
            setRows={setPieces2D}
            columns={[
              { key: "width", label: "Ancho (X)", placeholder: "800" },
              { key: "height", label: "Alto (Y)", placeholder: "600" },
              { key: "quantity", label: "Cantidad", placeholder: "4" },
            ]}
            newRow={() => ({ width: "", height: "", quantity: "" })}
          />
          <EditableTable
            title="Tableros disponibles"
            hint="Deja la cantidad vacía si tienes todos los que necesites."
            rows={stock2D}
            setRows={setStock2D}
            columns={[
              { key: "width", label: "Ancho (X)", placeholder: "2440" },
              { key: "height", label: "Alto (Y)", placeholder: "1220" },
              { key: "quantity", label: "Cantidad (opcional)", placeholder: "∞" },
            ]}
            newRow={() => ({ width: "", height: "", quantity: "" })}
          />
        </div>
      )}

      <section className="card inline">
        <label>
          Ancho de corte (sierra)
          <input
            type="number"
            min="0"
            step="any"
            value={kerf}
            onChange={(e) => setKerf(e.target.value)}
          />
        </label>

        {appMode === "1D" ? (
          <label>
            Método
            <select value={method1D} onChange={(e) => setMethod1D(e.target.value)}>
              <option value="fast">Rápido (heurística)</option>
              <option value="exact">Exacto (OR-Tools)</option>
            </select>
          </label>
        ) : (
          <label style={{ flexDirection: "row", alignItems: "center", gap: "8px" }}>
            <input 
              type="checkbox" 
              checked={allowRotation} 
              onChange={(e) => setAllowRotation(e.target.checked)} 
            />
            Permitir rotar piezas (90°)
          </label>
        )}

        <button onClick={calculate} disabled={loading}>
          {loading ? "Calculando…" : "Calcular plan de cortes"}
        </button>
      </section>

      {slow && (
        <div className="notice">
          Despertando el servidor… la primera vez del día puede tardar hasta un minuto. No cierres la página.
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {result && result.type === "1D" && (
        <section className="card">
          <h2>
            Resultado 1D
            {result.data.mode === "exact" && (
              <span className="badge">
                {result.data.proven_optimal ? "óptimo demostrado" : "mejor encontrado en el tiempo dado"}
              </span>
            )}
          </h2>
          <div className="stats">
            <div>
              <strong>{result.data.summary.total_bars}</strong>
              <span>barras</span>
            </div>
            <div>
              <strong>{result.data.summary.waste_percent}%</strong>
              <span>desperdicio</span>
            </div>
            <div>
              <strong>{fmt(result.data.summary.total_kerf_loss)}</strong>
              <span>perdido en sierra</span>
            </div>
          </div>
          <PlanDiagram bars={result.data.bars} />
          <button className="secondary" onClick={() => window.print()}>
            Imprimir plan
          </button>
        </section>
      )}

      {result && result.type === "2D" && (
        <section className="card">
          <h2>Resultado 2D (Tableros)</h2>
          <div className="stats">
            <div>
              <strong>{result.data.boards.length}</strong>
              <span>tableros usados</span>
            </div>
          </div>
          <PlanDiagram2D boards={result.data.boards} />
          <button className="secondary" onClick={() => window.print()}>
            Imprimir plan
          </button>
        </section>
      )}
    </main>
  );
}