async function fetchData() {
    try {
        const response = await fetch('/api/interactions'); // Fetch data from backend
        const data = await response.json();
        
        const xValues = [];
        const yValues = [];

        Object.keys(data).sort().forEach(month => {
            xValues.push(new Date(month).toLocaleString('default', { month: 'long', year: 'numeric' }));
            yValues.push(data[month]);
        });

        console.log("Chart Data:", { xValues, yValues });

        // Initialize Chart
        new Chart("myChart", {
            type: "bar",
            data: {
                labels: xValues,
                datasets: [{
                    backgroundColor: [ "rgba(0,0,255,0.6)", "rgba(0,0,255,0.6)", "rgba(0,0,255,0.6)", "rgba(0,0,255,0.6)","rgba(0,0,255,1.0)",],
                    data: yValues
                }]
            },
            options: {
                legend: { display: false },
                title: {
                    display: true,
                    text: "Chatbot Interactions"
                }
            }
        });
    } catch (error) {
        console.error("Error fetching interaction data:", error);
    }
}


async function fetchTopCategories() {
    try {
      const response = await fetch('/api/categories');
      const data = await response.json();
  
      const sorted = Object.entries(data)
        .sort(([, a], [, b]) => b - a)
        .filter(([, count]) => count > 0); // remove categories with 0
  
      const total = sorted.reduce((sum, [, count]) => sum + count, 0);
      const top3 = sorted.slice(0, 3); // show only top 3
  
      const list = document.querySelector(".frequently-asked ul");
      list.innerHTML = ""; // clear previous
  
      top3.forEach(([category, count]) => {
        const percentage = ((count / total) * 100).toFixed(1);
        const label = category.replace(/_/g, ' '); // optional formatting
        list.innerHTML += `<li>${label} <span>${percentage}%</span></li>`;
      });
    } catch (err) {
      console.error("Error fetching top categories:", err);
    }
  }

module.exports={
    fetchData,
    fetchTopCategories
}