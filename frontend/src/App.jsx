import React, { useState } from "react";
import { optimizeCuts } from "./api.js";
import PlanDiagram from "./PlanDiagram.jsx";

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
  const [pieces, setPieces] = useState([
    { length: "1250", quantity: "8" },
    { length: "830", quantity: "10" },
    { length: "410", quantity: "14" },
  ]);
  const [stock, setStock] = useState([{ length: "6000", quantity: "" }]);
  const [kerf, setKerf] = useState("3");
  const [mode, setMode] = useState("fast");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [slow, setSlow] = useState(false);

  const calculate = async () => {
    setError("");
    setResult(null);
    setSlow(false);
    const payload = {
      pieces: pieces
        .filter((p) => p.length && p.quantity)
        .map((p) => ({ length: Number(p.length), quantity: Number(p.quantity) })),
      stock: stock
        .filter((s) => s.length)
        .map((s) => ({
          length: Number(s.length),
          quantity: s.quantity === "" ? null : Number(s.quantity),
        })),
      kerf: Number(kerf || 0),
      mode,
    };
    if (!payload.pieces.length || !payload.stock.length) {
      setError("Agrega al menos una pieza y una barra.");
      return;
    }
    setLoading(true);
    // El hosting gratuito "duerme" el servidor; la primera visita puede tardar.
    const slowTimer = setTimeout(() => setSlow(true), 4000);
    try {
      setResult(await optimizeCuts(payload));
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
        <p>Corte lineal (tubos, perfiles, barras). Usa la misma unidad en todo (ej. mm).</p>
      </header>

      <div className="grid">
        <EditableTable
          title="Piezas a cortar"
          rows={pieces}
          setRows={setPieces}
          columns={[
            { key: "length", label: "Largo", placeholder: "1250" },
            { key: "quantity", label: "Cantidad", placeholder: "8" },
          ]}
          newRow={() => ({ length: "", quantity: "" })}
        />
        <EditableTable
          title="Barras disponibles"
          hint="Deja la cantidad vacía si tienes todas las que necesites."
          rows={stock}
          setRows={setStock}
          columns={[
            { key: "length", label: "Largo", placeholder: "6000" },
            { key: "quantity", label: "Cantidad (opcional)", placeholder: "∞" },
          ]}
          newRow={() => ({ length: "", quantity: "" })}
        />
      </div>

      <section className="card inline">
        <label>
          Ancho de corte de la sierra
          <input
            type="number"
            min="0"
            step="any"
            value={kerf}
            onChange={(e) => setKerf(e.target.value)}
          />
        </label>
        <label>
          Método
          <select value={mode} onChange={(e) => setMode(e.target.value)}>
            <option value="fast">Rápido (heurística)</option>
            <option value="exact">Exacto (OR-Tools)</option>
          </select>
        </label>
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

      {result && (
        <section className="card">
          <h2>
            Resultado
            {result.mode === "exact" && (
              <span className="badge">
                {result.proven_optimal ? "óptimo demostrado" : "mejor encontrado en el tiempo dado"}
              </span>
            )}
          </h2>
          <div className="stats">
            <div>
              <strong>{result.summary.total_bars}</strong>
              <span>barras</span>
            </div>
            <div>
              <strong>{result.summary.waste_percent}%</strong>
              <span>desperdicio</span>
            </div>
            <div>
              <strong>{fmt(result.summary.total_kerf_loss)}</strong>
              <span>perdido en sierra</span>
            </div>
            <div>
              <strong>{fmt(result.summary.total_leftover)}</strong>
              <span>en sobrantes</span>
            </div>
          </div>
          <p className="hint">
            Por largo:{" "}
            {result.summary.bars_by_length
              .map((b) => `${b.count} × ${fmt(b.stock_length)}`)
              .join(" · ")}
          </p>
          <PlanDiagram bars={result.bars} />
          <button className="secondary" onClick={() => window.print()}>
            Imprimir plan
          </button>
        </section>
      )}
    </main>
  );
}
