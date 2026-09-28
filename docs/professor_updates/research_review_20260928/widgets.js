(() => {
	const root = document.getElementById("w-viewer");
	if (!root) return;

	const $ = (id) => document.getElementById(id);
	const modelOrder = ["time250", "time1000", "pca8"];
	const expectedIds = [];
	for (const prefix of [
		"endpoint-time_t1-step250",
		"endpoint-time_t1-step1000",
		"endpoint-pca8",
	]) {
		for (const seed of [0, 1, 2]) expectedIds.push(`${prefix}-seed${seed}`);
	}
	const colors = [
		"#0f766e",
		"#2563eb",
		"#0891b2",
		"#7c3aed",
		"#c2410c",
		"#9a6700",
	];
	let data;
	let run;
	let yaw = -0.55;
	let pitch = 0.32;
	let zoom = 1;
	let hover = null;
	let dragging = null;
	const controls = {
		model: $("w-model"),
		seed: $("w-seed"),
		color: $("w-color"),
		reset: $("w-reset"),
		meta: $("w-meta"),
		legend: $("w-legend"),
		hover: $("w-hover"),
		stats: $("w-stats"),
		train: $("w-train-canvas"),
		development: $("w-development-canvas"),
	};
	const defaultHoverText =
		"Hover or touch near a dot for the nearest saved point.";

	function fail(message) {
		const alert = document.createElement("div");
		alert.className = "w-error-box";
		alert.setAttribute("role", "alert");
		alert.textContent = `Widget data error: ${message}`;
		root.replaceChildren(alert);
		throw new Error(`w-viewer: ${message}`);
	}

	function require(condition, message) {
		if (!condition) fail(message);
	}

	function finite(value) {
		return typeof value === "number" && Number.isFinite(value);
	}

	function fmt(value, digits = 3) {
		return finite(value) ? value.toFixed(digits) : "n/a";
	}

	function validateSplit(split, expectedCount, label) {
		require(split && split.count === expectedCount, `${label} count mismatch`);
		require(Array.isArray(split.coords) &&
			split.coords.length === expectedCount, `${label} coords missing`);
		require(Array.isArray(split.labels) &&
			split.labels.length === expectedCount, `${label} labels missing`);
		require(Array.isArray(split.reuse) &&
			split.reuse.length === expectedCount, `${label} reuse missing`);
		require(finite(split.retainedEnergy), `${label} retained energy missing`);
		require(Array.isArray(split.pcFractions) &&
			split.pcFractions.length === 3 &&
			split.pcFractions.every(finite), `${label} PC fractions missing`);
		require(split.support &&
			Number.isInteger(
				split.support.uniqueSourcesUsed,
			), `${label} support missing`);
		split.coords.forEach((point, index) => {
			require(Array.isArray(point) &&
				point.length === 3 &&
				point.every(finite), `${label} non-finite coordinate ${index}`);
			require(Number.isInteger(split.labels[index]) &&
				split.labels[index] >= 0 &&
				split.labels[index] < 30, `${label} label ${index} out of range`);
			require(finite(split.reuse[index]), `${label} reuse ${index} non-finite`);
		});
	}

	function validateData(payload) {
		require(payload && payload.version === 1, "missing payload version 1");
		require(JSON.stringify(payload.sourceRunIds) ===
			JSON.stringify(expectedIds), "source run IDs changed");
		require(Array.isArray(payload.pairs) &&
			payload.pairs.length === 30, "endpoint pairs missing");
		require(Array.isArray(payload.runs) &&
			payload.runs.length === 9, "expected exactly 9 curated runs");
		const seen = new Set();
		for (const item of payload.runs) {
			require(expectedIds.includes(
				item.id,
			), `unexpected run id ${item && item.id}`);
			require(modelOrder.includes(
				item.model,
			), `unexpected model ${item && item.model}`);
			require([0, 1, 2].includes(
				item.seed,
			), `unexpected seed ${item && item.seed}`);
			require(!seen.has(
				`${item.model}:${item.seed}`,
			), `duplicate model/seed ${item.model}:${item.seed}`);
			seen.add(`${item.model}:${item.seed}`);
			require(finite(item.extent) &&
				item.extent > 0, `bad extent for ${item.id}`);
			validateSplit(item.splits && item.splits.train, 480, `${item.id}.train`);
			validateSplit(
				item.splits && item.splits.development,
				240,
				`${item.id}.development`,
			);
		}
		for (const model of modelOrder)
			for (const seed of [0, 1, 2])
				require(seen.has(
					`${model}:${seed}`,
				), `missing selection ${model}/${seed}`);
	}

	function loadData() {
		const dataEl = $("w-data");
		require(dataEl, "missing #w-data JSON script");
		try {
			data = JSON.parse(dataEl.textContent);
		} catch (error) {
			fail(`malformed #w-data JSON: ${error.message}`);
		}
		validateData(data);
	}

	function setOptions(select, entries, fallback) {
		const previous = select.value;
		select.replaceChildren();
		for (const [value, label] of entries) {
			const option = document.createElement("option");
			option.value = value;
			option.textContent = label;
			select.append(option);
		}
		select.value = entries.some(([value]) => value === previous)
			? previous
			: fallback;
	}

	function resetGeneratedDom() {
		setOptions(
			controls.model,
			[
				["time250", "CEBRA-Time · step 250"],
				["time1000", "CEBRA-Time · step 1000"],
				["pca8", "PCA8 saved baseline"],
			],
			"time250",
		);
		setOptions(
			controls.seed,
			[
				["0", "0"],
				["1", "1"],
				["2", "2"],
			],
			"0",
		);
		setOptions(
			controls.color,
			[
				["goal", "Goal"],
				["start", "Start"],
			],
			"goal",
		);
		controls.legend.replaceChildren();
		controls.stats.replaceChildren();
		controls.meta.textContent = "";
		controls.hover.textContent = defaultHoverText;
	}

	function pickRun() {
		const model = controls.model.value;
		const seed = Number(controls.seed.value);
		run = data.runs.find((item) => item.model === model && item.seed === seed);
		require(run, `absent selection ${model}/${seed}`);
		hover = null;
		controls.hover.textContent = defaultHoverText;
		draw();
		updateText();
	}

	function pairFor(label) {
		const pair = data.pairs[label];
		require(Array.isArray(pair) &&
			pair.length === 2, `bad endpoint label ${label}`);
		return pair;
	}

	function colorValue(label) {
		const pair = pairFor(label);
		return controls.color.value === "start" ? pair[0] - 1 : pair[1] - 1;
	}

	function colorFor(label) {
		return colors[colorValue(label) % colors.length];
	}

	function rotate(point) {
		const cy = Math.cos(yaw);
		const sy = Math.sin(yaw);
		const cp = Math.cos(pitch);
		const sp = Math.sin(pitch);
		const x = point[0] * cy + point[2] * sy;
		const z = -point[0] * sy + point[2] * cy;
		return [x, point[1] * cp - z * sp, point[1] * sp + z * cp];
	}

	function canvasSize(canvas) {
		const rect = canvas.getBoundingClientRect();
		const ratio = window.devicePixelRatio || 1;
		canvas.width = Math.max(1, Math.round(rect.width * ratio));
		canvas.height = Math.max(1, Math.round(rect.height * ratio));
		const ctx = canvas.getContext("2d");
		ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
		return { ctx, width: rect.width, height: rect.height };
	}

	function project(point, width, height) {
		const q = rotate(point);
		const scale = (0.42 * Math.min(width, height) * zoom) / run.extent;
		return {
			x: width / 2 + q[0] * scale,
			y: height / 2 - q[1] * scale,
			z: q[2],
		};
	}

	function drawAxes(ctx, width, height) {
		const origin = project([0, 0, 0], width, height);
		const axes = [
			{ label: "PC1", point: [run.extent * 0.62, 0, 0], color: "#2563eb" },
			{ label: "PC2", point: [0, run.extent * 0.62, 0], color: "#0f766e" },
			{ label: "PC3", point: [0, 0, run.extent * 0.62], color: "#7c3aed" },
		];
		ctx.lineWidth = 1.4;
		ctx.font = "12px system-ui, sans-serif";
		for (const axis of axes) {
			const tip = project(axis.point, width, height);
			ctx.strokeStyle = axis.color;
			ctx.fillStyle = axis.color;
			ctx.beginPath();
			ctx.moveTo(origin.x, origin.y);
			ctx.lineTo(tip.x, tip.y);
			ctx.stroke();
			ctx.fillText(axis.label, tip.x + 5, tip.y - 5);
		}
	}

	function drawPanel(splitName) {
		const canvas = controls[splitName];
		const split = run.splits[splitName];
		const { ctx, width, height } = canvasSize(canvas);
		ctx.clearRect(0, 0, width, height);
		ctx.fillStyle = "#fffdf7";
		ctx.fillRect(0, 0, width, height);
		const points = split.coords.map((point, index) => ({
			index,
			screen: project(point, width, height),
		}));
		points.sort((a, b) => a.screen.z - b.screen.z);
		for (const item of points) {
			const label = split.labels[item.index];
			ctx.globalAlpha = 0.72;
			ctx.fillStyle = colorFor(label);
			ctx.beginPath();
			ctx.arc(item.screen.x, item.screen.y, 3.1, 0, Math.PI * 2);
			ctx.fill();
		}
		ctx.globalAlpha = 1;
		drawAxes(ctx, width, height);
		if (hover && hover.split === splitName) {
			const screen = project(split.coords[hover.index], width, height);
			ctx.strokeStyle = "#111827";
			ctx.lineWidth = 2;
			ctx.beginPath();
			ctx.arc(screen.x, screen.y, 7, 0, Math.PI * 2);
			ctx.stroke();
		}
		ctx.fillStyle = "#17324d";
		ctx.font = "12px system-ui, sans-serif";
		ctx.fillText(
			`${split.count} complete-cue dots · shared orthographic view`,
			12,
			20,
		);
		canvas.dataset.drawn = "true";
	}

	function draw() {
		if (!run) return;
		drawPanel("train");
		drawPanel("development");
	}

	function describePoint(splitName, index) {
		const split = run.splits[splitName];
		const point = split.coords[index];
		const [start, goal] = pairFor(split.labels[index]);
		return `${splitName} row ${index}: start ${start}, goal ${goal}, PC=(${point.map((v) => fmt(v, 2)).join(", ")}), mean source reuse ${fmt(split.reuse[index], 2)}`;
	}

	function nearest(splitName, event) {
		const canvas = controls[splitName];
		const split = run.splits[splitName];
		const rect = canvas.getBoundingClientRect();
		const width = rect.width;
		const height = rect.height;
		const x = event.clientX - rect.left;
		const y = event.clientY - rect.top;
		let best = null;
		let bestD2 = Infinity;
		for (let i = 0; i < split.coords.length; i += 1) {
			const screen = project(split.coords[i], width, height);
			const d2 = (screen.x - x) ** 2 + (screen.y - y) ** 2;
			if (d2 < bestD2) {
				best = i;
				bestD2 = d2;
			}
		}
		if (best !== null && bestD2 <= 16 ** 2) {
			hover = { split: splitName, index: best };
			controls.hover.textContent = describePoint(splitName, best);
		} else {
			hover = null;
			controls.hover.textContent = defaultHoverText;
		}
		draw();
	}

	function updateLegend() {
		controls.legend.replaceChildren();
		const label = controls.color.value === "start" ? "Start" : "Goal";
		for (let i = 0; i < 6; i += 1) {
			const item = document.createElement("span");
			const swatch = document.createElement("i");
			swatch.className = "w-swatch";
			swatch.style.background = colors[i];
			item.append(swatch, document.createTextNode(`${label} ${i + 1}`));
			controls.legend.append(item);
		}
	}

	function splitRow(splitName) {
		const split = run.splits[splitName];
		const support = split.support;
		const row = document.createElement("tr");
		const values = [
			splitName,
			split.count,
			`${(100 * split.retainedEnergy).toFixed(1)}%`,
			`${support.uniqueSourcesUsed} sources; max reuse ${support.maxSourceReuse}; mean reuse range ${support.meanSourceReusePerRowRange.map((v) => fmt(v, 2)).join("–")}`,
		];
		values.forEach((value, index) => {
			const cell = document.createElement(index ? "td" : "th");
			if (!index) cell.scope = "row";
			cell.textContent = String(value);
			row.append(cell);
		});
		return row;
	}

	function updateText() {
		controls.meta.textContent = `${run.modelLabel}; seed ${run.seed}. Saved whole-cue projection: ${run.projection}; ambient dimension ${run.ambientDimension}. No decoder scores are shown.`;
		const table = document.createElement("table");
		const header = table.createTHead().insertRow();
		for (const label of [
			"Split",
			"Dots",
			"Energy retained by saved training PCs 1–3",
			"Support / source reuse caveat",
		]) {
			const cell = document.createElement("th");
			cell.scope = "col";
			cell.textContent = label;
			header.append(cell);
		}
		table.createTBody().append(splitRow("train"), splitRow("development"));
		const note = document.createElement("p");
		note.className = "w-note";
		note.textContent =
			"Support counts describe reused real sources, not independent simultaneous recordings. Training and development sources are separated in the saved atlas; development was already exposed during earlier work.";
		controls.stats.replaceChildren(table, note);
		updateLegend();
	}

	function reset() {
		yaw = -0.55;
		pitch = 0.32;
		zoom = 1;
		hover = null;
		controls.hover.textContent = defaultHoverText;
		draw();
	}

	function onKey(event) {
		if (
			![
				"ArrowLeft",
				"ArrowRight",
				"ArrowUp",
				"ArrowDown",
				"+",
				"=",
				"-",
				"Home",
			].includes(event.key)
		)
			return;
		event.preventDefault();
		if (event.key === "Home") {
			reset();
			return;
		}
		if (event.key === "ArrowLeft") yaw -= 0.1;
		if (event.key === "ArrowRight") yaw += 0.1;
		if (event.key === "ArrowUp") pitch -= 0.1;
		if (event.key === "ArrowDown") pitch += 0.1;
		if (event.key === "+" || event.key === "=") zoom = Math.min(8, zoom * 1.12);
		if (event.key === "-") zoom = Math.max(0.25, zoom / 1.12);
		draw();
	}

	function wireCanvas(splitName) {
		const canvas = controls[splitName];
		canvas.addEventListener("pointerdown", (event) => {
			nearest(splitName, event);
			dragging = { id: event.pointerId, x: event.clientX, y: event.clientY };
			canvas.setPointerCapture(event.pointerId);
		});
		canvas.addEventListener("pointermove", (event) => {
			if (dragging && dragging.id === event.pointerId) {
				yaw += (event.clientX - dragging.x) * 0.008;
				pitch += (event.clientY - dragging.y) * 0.008;
				dragging = { id: event.pointerId, x: event.clientX, y: event.clientY };
				draw();
			} else {
				nearest(splitName, event);
			}
		});
		canvas.addEventListener("pointerup", () => {
			dragging = null;
		});
		canvas.addEventListener("pointercancel", () => {
			dragging = null;
		});
		canvas.addEventListener("pointerleave", () => {
			if (!dragging) {
				hover = null;
				controls.hover.textContent = defaultHoverText;
				draw();
			}
		});
		canvas.addEventListener(
			"wheel",
			(event) => {
				event.preventDefault();
				zoom = Math.min(
					8,
					Math.max(0.25, zoom * Math.exp(-event.deltaY * 0.001)),
				);
				draw();
			},
			{ passive: false },
		);
		canvas.addEventListener("keydown", onKey);
	}

	for (const value of Object.values(controls))
		require(value, "missing one or more w-* controls");
	loadData();
	resetGeneratedDom();
	controls.model.addEventListener("change", pickRun);
	controls.seed.addEventListener("change", pickRun);
	controls.color.addEventListener("change", () => {
		draw();
		updateLegend();
	});
	controls.reset.addEventListener("click", reset);
	window.addEventListener("resize", draw);
	wireCanvas("train");
	wireCanvas("development");
	pickRun();
	root.dataset.ready = "true";
})();
