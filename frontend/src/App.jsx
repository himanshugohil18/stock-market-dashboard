import { useEffect, useState } from "react";

const API_URL =
  "https://hp2m8veeog.execute-api.ap-south-1.amazonaws.com/stocks";

function App() {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function getStocks() {
    try {
      setLoading(true);

      const response = await fetch(API_URL);

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }

      const data = await response.json();

      setStocks(data.stocks || []);
      setError("");
    } catch (err) {
      console.error(err);
      setError("Failed to load stock data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    getStocks();
  }, []);

  return (
    <div style={styles.app}>
      <header style={styles.header}>
        <div>
          <h1 style={styles.title}>📈 Stock Market Dashboard</h1>
          <p style={styles.subtitle}>
            Real-time data from AWS Lambda + API Gateway + DynamoDB
          </p>
        </div>

        <button style={styles.refreshButton} onClick={getStocks}>
          🔄 Refresh
        </button>
      </header>

      <section style={styles.stats}>
        <div style={styles.card}>
          <div style={styles.cardLabel}>Total Records</div>
          <div style={styles.cardValue}>{stocks.length}</div>
        </div>

        <div style={styles.card}>
          <div style={styles.cardLabel}>Symbol</div>
          <div style={styles.cardValue}>
            {stocks.length > 0 ? stocks[0].symbol : "-"}
          </div>
        </div>

        <div style={styles.card}>
          <div style={styles.cardLabel}>Exchange</div>
          <div style={styles.cardValue}>
            {stocks.length > 0 ? stocks[0].exchange : "-"}
          </div>
        </div>

        <div style={styles.card}>
          <div style={styles.cardLabel}>Latest Price</div>
          <div style={styles.cardValue}>
            ₹{stocks.length > 0 ? stocks[0].price : "-"}
          </div>
        </div>
      </section>

      <section style={styles.tableContainer}>
        <div style={styles.tableHeader}>
          <h2>Market Data</h2>
          {loading && <span>Loading...</span>}
        </div>

        {error && <div style={styles.error}>{error}</div>}

        {!loading && !error && stocks.length === 0 && (
          <div style={styles.empty}>No stock data found.</div>
        )}

        {!loading && stocks.length > 0 && (
          <div style={styles.tableWrapper}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Symbol</th>
                  <th style={styles.th}>Exchange</th>
                  <th style={styles.th}>Price</th>
                  <th style={styles.th}>Token</th>
                  <th style={styles.th}>Sequence</th>
                  <th style={styles.th}>Received At</th>
                </tr>
              </thead>

              <tbody>
                {stocks.slice(0, 100).map((stock, index) => (
                  <tr key={index}>
                    <td style={styles.td}>
                      <strong>{stock.symbol}</strong>
                    </td>

                    <td style={styles.td}>
                      <span style={styles.exchange}>
                        {stock.exchange}
                      </span>
                    </td>

                    <td style={styles.price}>
                      ₹{stock.price}
                    </td>

                    <td style={styles.td}>{stock.token}</td>

                    <td style={styles.td}>
                      {stock.sequence_number}
                    </td>

                    <td style={styles.td}>
                      {stock.received_at
                        ? new Date(
                            stock.received_at * 1000
                          ).toLocaleString()
                        : "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {stocks.length > 100 && (
          <p style={styles.footer}>
            Showing first 100 records out of {stocks.length}.
          </p>
        )}
      </section>
    </div>
  );
}

const styles = {
  app: {
    minHeight: "100vh",
    background: "#0f172a",
    color: "#e2e8f0",
    padding: "30px",
    fontFamily: "Arial, sans-serif",
  },

  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "30px",
  },

  title: {
    margin: 0,
    fontSize: "32px",
  },

  subtitle: {
    color: "#94a3b8",
    marginTop: "8px",
  },

  refreshButton: {
    background: "#2563eb",
    color: "white",
    border: "none",
    padding: "12px 20px",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "15px",
  },

  stats: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: "20px",
    marginBottom: "30px",
  },

  card: {
    background: "#1e293b",
    padding: "22px",
    borderRadius: "12px",
    border: "1px solid #334155",
  },

  cardLabel: {
    color: "#94a3b8",
    fontSize: "14px",
    marginBottom: "10px",
  },

  cardValue: {
    fontSize: "25px",
    fontWeight: "bold",
  },

  tableContainer: {
    background: "#1e293b",
    borderRadius: "12px",
    border: "1px solid #334155",
    overflow: "hidden",
  },

  tableHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "20px",
    borderBottom: "1px solid #334155",
  },

  tableWrapper: {
    overflowX: "auto",
  },

  table: {
    width: "100%",
    borderCollapse: "collapse",
  },

  th: {
    textAlign: "left",
    padding: "15px",
    background: "#0f172a",
    color: "#94a3b8",
    fontSize: "13px",
  },

  td: {
    padding: "15px",
    borderTop: "1px solid #334155",
    color: "#cbd5e1",
  },

  price: {
    padding: "15px",
    borderTop: "1px solid #334155",
    color: "#22c55e",
    fontWeight: "bold",
  },

  exchange: {
    background: "#334155",
    padding: "5px 9px",
    borderRadius: "5px",
    fontSize: "12px",
  },

  error: {
    padding: "20px",
    color: "#ef4444",
  },

  empty: {
    padding: "40px",
    textAlign: "center",
    color: "#94a3b8",
  },

  footer: {
    padding: "15px 20px",
    color: "#94a3b8",
    fontSize: "13px",
  },
};

export default App;
