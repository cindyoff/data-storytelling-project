const data = [
  {
    name: "Alice",
    values: {
      Technique: 8,
      Créativité: 6,
      Leadership: 7,
      Communication: 9,
      Rigueur: 5
    }
  },
  {
    name: "Bruno",
    values: {
      Technique: 6,
      Créativité: 9,
      Leadership: 5,
      Communication: 6,
      Rigueur: 8
    }
  },
  {
    name: "Chloé",
    values: {
      Technique: 9,
      Créativité: 7,
      Leadership: 8,
      Communication: 5,
      Rigueur: 7
    }
  },
  {
    name: "David",
    values: {
      Technique: 5,
      Créativité: 5,
      Leadership: 9,
      Communication: 8,
      Rigueur: 6
    }
  }
];

const dimensions = ["Technique", "Créativité", "Leadership", "Communication", "Rigueur"];
const maxValue = 10;
const levels = 5;

const width = 700;
const height = 700;
const margin = 80;
const radius = Math.min(width, height) / 2 - margin;

const color = d3.scaleOrdinal()
  .domain(data.map(d => d.name))
  .range(["#2563eb", "#ef4444", "#10b981", "#f59e0b"]);

const angleSlice = (Math.PI * 2) / dimensions.length;
const rScale = d3.scaleLinear()
  .domain([0, maxValue])
  .range([0, radius]);

const svg = d3.select("#chart")
  .append("svg")
  .attr("width", width)
  .attr("height", height);

const g = svg.append("g")
  .attr("transform", `translate(${width / 2}, ${height / 2})`);

const tooltip = d3.select("body")
  .append("div")
  .attr("class", "tooltip");

// =====================
// SELECTS
// =====================
const person1Select = d3.select("#person1");
const person2Select = d3.select("#person2");

data.forEach(d => {
  person1Select.append("option").attr("value", d.name).text(d.name);
  person2Select.append("option").attr("value", d.name).text(d.name);
});

person1Select.property("value", "Alice");
person2Select.property("value", "Bruno");

// =====================
// FOND / GRILLE
// =====================
for (let level = 1; level <= levels; level++) {
  const levelRadius = radius * (level / levels);

  const points = dimensions.map((dim, i) => {
    const angle = i * angleSlice - Math.PI / 2;
    return [
      levelRadius * Math.cos(angle),
      levelRadius * Math.sin(angle)
    ];
  });

  g.append("polygon")
    .attr("class", "grid-circle")
    .attr("points", points.map(p => p.join(",")).join(" "))
    .attr("stroke-width", 1);

  g.append("text")
    .attr("class", "grid-label")
    .attr("x", 4)
    .attr("y", -levelRadius)
    .text((maxValue / levels) * level);
}

// Axes
dimensions.forEach((dim, i) => {
  const angle = i * angleSlice - Math.PI / 2;
  const x = rScale(maxValue) * Math.cos(angle);
  const y = rScale(maxValue) * Math.sin(angle);

  g.append("line")
    .attr("class", "axis-line")
    .attr("x1", 0)
    .attr("y1", 0)
    .attr("x2", x)
    .attr("y2", y);

  const labelOffset = 22;
  g.append("text")
    .attr("class", "axis-label")
    .attr("x", (rScale(maxValue) + labelOffset) * Math.cos(angle))
    .attr("y", (rScale(maxValue) + labelOffset) * Math.sin(angle))
    .attr("text-anchor", "middle")
    .attr("dominant-baseline", "middle")
    .text(dim);
});

// =====================
// GENERATEUR DE LIGNE RADAR
// =====================
const radarLine = d3.lineRadial()
  .radius(d => rScale(d.value))
  .angle((d, i) => i * angleSlice)
  .curve(d3.curveLinearClosed);

// Groupe pour les séries
const radarWrapper = g.append("g").attr("class", "radar-wrapper");

// =====================
// UTILITAIRE
// =====================
function formatPerson(person) {
  return dimensions.map(dim => ({
    axis: dim,
    value: person.values[dim]
  }));
}

// =====================
// RENDER
// =====================
function updateChart(selectedNames) {
  const selectedData = data.filter(d => selectedNames.includes(d.name));

  // JOIN série
  const series = radarWrapper.selectAll(".radar-series")
    .data(selectedData, d => d.name);

  const seriesEnter = series.enter()
    .append("g")
    .attr("class", "radar-series");

  // Zone
  seriesEnter.append("path")
    .attr("class", "radar-area")
    .attr("fill", d => color(d.name))
    .attr("stroke", d => color(d.name))
    .attr("d", d => {
      const zeroData = dimensions.map(dim => ({ axis: dim, value: 0 }));
      return radarLine(zeroData);
    });

  // Points
  seriesEnter.each(function(person) {
    const pointsData = formatPerson(person);

    d3.select(this)
      .selectAll(".radar-point")
      .data(pointsData)
      .enter()
      .append("circle")
      .attr("class", "radar-point")
      .attr("r", 0)
      .attr("fill", color(person.name))
      .attr("cx", 0)
      .attr("cy", 0);
  });

  const mergedSeries = seriesEnter.merge(series);

  // Animate area
  mergedSeries.select(".radar-area")
    .transition()
    .duration(900)
    .ease(d3.easeCubicOut)
    .attrTween("d", function(person) {
      const previous = this._current || dimensions.map(dim => ({ axis: dim, value: 0 }));
      const next = formatPerson(person);
      const interpolate = d3.interpolate(previous, next);
      this._current = next;

      return function(t) {
        return radarLine(interpolate(t));
      };
    });

  // Animate points
  mergedSeries.each(function(person) {
    const pointsData = formatPerson(person);

    d3.select(this)
      .selectAll(".radar-point")
      .data(pointsData)
      .join("circle")
      .attr("class", "radar-point")
      .attr("fill", color(person.name))
      .on("mousemove", function(event, d) {
        tooltip
          .style("opacity", 1)
          .html(`<strong>${person.name}</strong><br>${d.axis} : ${d.value}/${maxValue}`)
          .style("left", (event.pageX + 12) + "px")
          .style("top", (event.pageY - 20) + "px");
      })
      .on("mouseleave", function() {
        tooltip.style("opacity", 0);
      })
      .transition()
      .duration(900)
      .ease(d3.easeCubicOut)
      .attr("r", 5)
      .attr("cx", (d, i) => {
        const angle = i * angleSlice - Math.PI / 2;
        return rScale(d.value) * Math.cos(angle);
      })
      .attr("cy", (d, i) => {
        const angle = i * angleSlice - Math.PI / 2;
        return rScale(d.value) * Math.sin(angle);
      });
  });

  // Exit
  series.exit()
    .transition()
    .duration(500)
    .style("opacity", 0)
    .remove();

  updateLegend(selectedData);
}

function updateLegend(selectedData) {
  const legend = d3.select("#legend");

  const items = legend.selectAll(".legend-item")
    .data(selectedData, d => d.name);

  const itemsEnter = items.enter()
    .append("div")
    .attr("class", "legend-item");

  itemsEnter.append("div")
    .attr("class", "legend-color");

  itemsEnter.append("div")
    .attr("class", "legend-label");

  itemsEnter.merge(items)
    .select(".legend-color")
    .style("background", d => color(d.name));

  itemsEnter.merge(items)
    .select(".legend-label")
    .text(d => d.name);

  items.exit().remove();
}

function refresh() {
  const p1 = person1Select.property("value");
  const p2 = person2Select.property("value");

  const selected = p1 === p2 ? [p1] : [p1, p2];
  updateChart(selected);
}

person1Select.on("change", refresh);
person2Select.on("change", refresh);

refresh();