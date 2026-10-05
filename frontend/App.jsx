import { useEffect, useState } from "react";

const API_URL =
  "https://hp2m8veeog.execute-api.ap-south-1.amazonaws.com/stocks";

function App() {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function getStocks() {
      try {
        const response = await fetch(API_URL);

        if (!response.ok) {
          throw new Error(`HTTP error: ${response.status}`);
        }

        const data = await response.json();

        console.log("Stock count:", data.count);
        console.log("Stocks:", data.stocks);

        setStocks(data.stocks);
      } catch (err) {
        console.error("Failed to fetch stocks:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    getStocks();
  }, []);

  if (loading) {
    return <h2>Loading stocks...</h2>;
  }

  if (error) {
    return <h2>Error: {error}</h2>;
  }

  return (
    <div style={{ padding: "30px" }}>
      <h1>📈 Stock Market Dashboard</h1>

      <p>Total Stocks: {stocks.length}</p>

      <table border="1" cellPadding="10">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Exchange</th>
            <th>Price</th>
            <th>Token</th>
          </tr>
        </thead>

        <tbody>
          {stocks.map((stock, index) => (
            <tr key={index}>
              <td>{stock.symbol}</td>
              <td>{stock.exchange}</td>
              <td>₹{stock.price}</td>
              <td>{stock.token}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
