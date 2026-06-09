/* ===========================================================================
   Interactive iPod (sect_ipod.html)

   Design:
   - The YouTube player is created ONCE at full size inside the screen and is
     never moved (moving an <iframe> reloads it, which both stops playback and
     trips YouTube's "An error occurred" state). It sits behind the menu so
     audio keeps playing while you browse, and is raised above the menu (via a
     CSS class) only while you're watching.
   - The SoundCloud widget is an off-screen audio-only iframe.
   - The screen is a small state machine: a stack of "views" (menu / list /
     nowplaying / reel). Now-playing title + description are shown in a panel
     beneath the device, where there's room to read them.
   =========================================================================== */
(function () {
	"use strict";

	var screenBody = document.getElementById("ipodScreenBody");
	if (!screenBody) {
		return; // not on the iPod page
	}

	var statusTitle = document.getElementById("ipodStatusTitle");
	var nowPlayingFlag = document.getElementById("ipodNowPlayingFlag");
	var device = document.getElementById("ipod");
	var wheel = document.getElementById("ipodWheel");
	var ytStage = document.getElementById("ytStage");

	var infoPanel = document.getElementById("ipodInfo");
	var infoSource = document.getElementById("ipodInfoSource");
	var infoTitle = document.getElementById("ipodInfoTitle");
	var infoDate = document.getElementById("ipodInfoDate");
	var infoDesc = document.getElementById("ipodInfoDesc");

	// Format a date string ("2025-04-23" or SoundCloud's "2015/04/22 ...") as
	// "Apr 23, 2025". Returns "" if it can't be parsed.
	function formatDate(s) {
		if (!s) return "";
		var d = new Date(s);
		if (isNaN(d.getTime())) { d = new Date(String(s).replace(/-/g, "/")); }
		if (isNaN(d.getTime())) return "";
		return d.toLocaleDateString(undefined, {
			year: "numeric", month: "short", day: "numeric"
		});
	}

	// ---- Data (injected by Django via json_script) -------------------------
	function readJson(id, fallback) {
		var el = document.getElementById(id);
		if (!el) return fallback;
		try {
			return JSON.parse(el.textContent);
		} catch (e) {
			return fallback;
		}
	}
	var ytData = readJson("ipod-youtube-data", []);
	var igData = readJson("ipod-instagram-data", []);
	var scUrl = readJson("ipod-soundcloud-url", "");

	// ---- Players (persistent) ----------------------------------------------
	var ytPlayer = null;
	var ytReady = false;
	var pendingYtId = null; // video selected before the API finished loading
	var scWidget = null;
	var scReady = false;
	var scSounds = []; // ascending (oldest -> newest); {title, widgetIndex, description}

	// What is currently playing, so the wheel's play/prev/next act on it.
	var active = { source: null, index: -1, playing: false };

	// ---- View stack --------------------------------------------------------
	var stack = [];

	function currentView() {
		return stack[stack.length - 1];
	}

	function pushView(view) {
		stack.push(view);
		render();
	}

	function popView() {
		if (stack.length > 1) {
			stack.pop();
			render();
		}
	}

	function makeListView(title, items) {
		return {
			type: "list",
			title: title,
			items: items,
			selectedIndex: items.length ? 0 : -1
		};
	}

	// ---- Sources (the main menu) -------------------------------------------
	var SOURCES = [
		{ id: "instagram", label: "UGG Chronicles", build: buildInstagramList },
		{ id: "youtube", label: "YouTube", build: buildYouTubeList },
		{ id: "soundcloud", label: "SoundCloud", build: buildSoundCloudList }
		// Future: { id: "recs", label: "Music Recommendations", build: buildRecsList }
	];

	function buildMainMenu() {
		var items = SOURCES.map(function (src) {
			return {
				label: src.label,
				drill: true,
				action: function () { pushView(src.build()); }
			};
		});
		return makeListView("Dipen's iPod", items);
	}

	function buildYouTubeList() {
		// Group videos by year (ytData is already newest-first), so the top
		// level is a short list of years and each drills into that year.
		var groups = {};
		var order = [];
		ytData.forEach(function (video, i) {
			var year = (video.date || "").slice(0, 4) || "Other";
			if (!groups[year]) { groups[year] = []; order.push(year); }
			groups[year].push(i); // keep the absolute index into ytData
		});
		var items = order.map(function (year) {
			return {
				label: year,
				drill: true,
				action: function () { pushView(buildYouTubeYear(year, groups[year])); }
			};
		});
		return makeListView("YouTube", items);
	}

	function buildYouTubeYear(year, indices) {
		var items = indices.map(function (idx) {
			return {
				label: ytData[idx].title || "Untitled",
				drill: true,
				action: function () { playYouTube(idx); }
			};
		});
		return makeListView("YouTube · " + year, items);
	}

	function buildSoundCloudList() {
		if (!scReady) {
			return { type: "loading", title: "SoundCloud", message: "Loading tracks…" };
		}
		var items = scSounds.map(function (sound, i) {
			return {
				label: sound.title,
				drill: true,
				action: function () { playSoundCloud(i); }
			};
		});
		return makeListView("SoundCloud", items);
	}

	function buildInstagramList() {
		var items = igData.map(function (reel, i) {
			return {
				label: reel.title || ("Reel " + (i + 1)),
				drill: true,
				action: function () { showReel(reel); }
			};
		});
		return makeListView("UGG Chronicles", items);
	}

	// ---- Rendering ---------------------------------------------------------
	function render() {
		var view = currentView();
		statusTitle.textContent = view.title || "iPod";
		nowPlayingFlag.hidden = !active.playing;

		// Only raise the video above the menu while watching a YouTube clip.
		var watching = view.type === "nowplaying" && view.source === "YouTube";
		if (ytStage) { ytStage.classList.toggle("is-visible", watching); }

		if (view.type === "list") {
			renderList(view);
		} else if (view.type === "loading") {
			renderMessage(view.message);
		} else if (view.type === "nowplaying") {
			renderNowPlaying(view);
		} else if (view.type === "reel") {
			renderReel(view);
		}
	}

	function renderMessage(message) {
		screenBody.innerHTML = "";
		var box = document.createElement("div");
		box.className = "ipod-view-empty";
		box.textContent = message;
		screenBody.appendChild(box);
	}

	function renderList(view) {
		screenBody.innerHTML = "";

		if (!view.items.length) {
			renderMessage("Nothing here yet — check back soon.");
			return;
		}

		var ul = document.createElement("ul");
		ul.className = "ipod-list";

		view.items.forEach(function (item, i) {
			var li = document.createElement("li");
			li.className = "ipod-row" + (i === view.selectedIndex ? " is-selected" : "");

			var label = document.createElement("span");
			label.className = "ipod-row-label";
			label.textContent = item.label;
			li.appendChild(label);

			if (item.drill) {
				var chev = document.createElement("span");
				chev.className = "ipod-row-chevron";
				chev.innerHTML = "&#8250;";
				li.appendChild(chev);
			}

			// Clicking a row selects AND opens it (so one click plays a track).
			li.addEventListener("click", function () {
				view.selectedIndex = i;
				render();
				item.action();
			});

			ul.appendChild(li);
		});

		screenBody.appendChild(ul);
		scrollSelectedIntoView();
	}

	function scrollSelectedIntoView() {
		var sel = screenBody.querySelector(".ipod-row.is-selected");
		if (sel && sel.scrollIntoView) {
			sel.scrollIntoView({ block: "nearest", behavior: "smooth" });
		}
	}

	function renderNowPlaying(view) {
		screenBody.innerHTML = "";
		// For YouTube the video layer covers the body, so we only need to render
		// the audio "now playing" card for SoundCloud.
		if (view.source === "YouTube") { return; }

		var wrap = document.createElement("div");
		wrap.className = "ipod-np" + (active.playing ? "" : " is-paused");

		var source = document.createElement("div");
		source.className = "ipod-np-source";
		source.textContent = view.source;
		wrap.appendChild(source);

		var title = document.createElement("div");
		title.className = "ipod-np-title";
		title.textContent = view.trackTitle;
		wrap.appendChild(title);

		var art = document.createElement("div");
		art.className = "ipod-np-art";
		for (var b = 0; b < 5; b++) {
			var bar = document.createElement("span");
			bar.className = "ipod-eq-bar";
			art.appendChild(bar);
		}
		wrap.appendChild(art);

		screenBody.appendChild(wrap);
	}

	function renderReel(view) {
		screenBody.innerHTML = "";
		if (!view.shortcode) {
			renderMessage("This reel isn't available.");
			return;
		}
		var iframe = document.createElement("iframe");
		iframe.className = "ipod-reel-frame";
		iframe.src = "https://www.instagram.com/reel/" +
			encodeURIComponent(view.shortcode) + "/embed/";
		iframe.allow = "autoplay; encrypted-media";
		iframe.setAttribute("allowfullscreen", "");
		screenBody.appendChild(iframe);
	}

	// ---- Now-playing info panel (below the device) -------------------------
	function updateInfo(source, title, description, date) {
		infoSource.textContent = source;
		infoTitle.textContent = title || "";
		var when = formatDate(date);
		infoDate.textContent = when ? "Uploaded " + when : "";
		infoDate.hidden = !when;
		infoDesc.textContent = description || "";
		infoDesc.hidden = !description;
		infoPanel.hidden = false;
	}

	// ---- Playback ----------------------------------------------------------
	function playYouTube(index) {
		var video = ytData[index];
		if (!video) return;
		active.source = "youtube";
		active.index = index;
		if (scWidget) { try { scWidget.pause(); } catch (e) {} }

		// Show the now-playing view first so the video layer is visible, then
		// load + play within the same click gesture (so autoplay is allowed).
		pushView({
			type: "nowplaying",
			title: "Now Playing",
			source: "YouTube",
			trackTitle: video.title || "Untitled"
		});

		if (ytReady && ytPlayer) {
			ytPlayer.loadVideoById(video.videoId);
			ytPlayer.playVideo();
		} else {
			pendingYtId = video.videoId;
		}
		updateInfo("YouTube", video.title, video.description, video.date);
	}

	function playSoundCloud(index) {
		var sound = scSounds[index];
		if (!sound || !scWidget) return;
		active.source = "soundcloud";
		active.index = index;
		if (ytPlayer && ytReady) { try { ytPlayer.pauseVideo(); } catch (e) {} }
		scWidget.skip(sound.widgetIndex);
		scWidget.play();
		pushView({
			type: "nowplaying",
			title: "Now Playing",
			source: "SoundCloud",
			trackTitle: sound.title
		});
		updateInfo("SoundCloud", sound.title, sound.description, sound.date);
	}

	function showReel(reel) {
		if (ytPlayer && ytReady) { try { ytPlayer.pauseVideo(); } catch (e) {} }
		if (scWidget) { try { scWidget.pause(); } catch (e) {} }
		pushView({ type: "reel", title: "UGG Chronicles", shortcode: reel.shortcode });
		updateInfo("UGG Chronicles", reel.title || "Reel",
			reel.caption || reel.description);
	}

	function togglePlayPause() {
		if (active.source === "youtube" && ytPlayer && ytReady) {
			var state = ytPlayer.getPlayerState();
			if (state === 1) { ytPlayer.pauseVideo(); } else { ytPlayer.playVideo(); }
		} else if (active.source === "soundcloud" && scWidget) {
			scWidget.toggle();
		}
	}

	function skipTrack(delta) {
		if (active.source === "youtube") {
			var next = active.index + delta;
			if (next >= 0 && next < ytData.length) { playYouTube(next); }
		} else if (active.source === "soundcloud") {
			var n = active.index + delta;
			if (n >= 0 && n < scSounds.length) { playSoundCloud(n); }
		}
	}

	function setPlaying(isPlaying) {
		active.playing = isPlaying;
		nowPlayingFlag.hidden = !isPlaying;
		var np = screenBody.querySelector(".ipod-np");
		if (np) { np.classList.toggle("is-paused", !isPlaying); }
	}

	// ---- Haptics -----------------------------------------------------------
	// Two devices, two mechanisms:
	//   - Android (and other Vibration-API browsers) honour navigator.vibrate.
	//   - iOS Safari ignores navigator.vibrate entirely; the only way to fire a
	//     system haptic from a page is to toggle an <input switch> (iOS 17.4+)
	//     inside a user gesture. The proven recipe (Gavin Nelson's ios-haptics)
	//     is to create a fresh display:none switch, click it, and remove it on
	//     every trigger — reusing one hidden element does NOT reliably fire it.
	function iosHaptic() {
		var label = document.createElement("label");
		label.setAttribute("aria-hidden", "true");
		label.style.display = "none";
		var input = document.createElement("input");
		input.type = "checkbox";
		input.setAttribute("switch", ""); // iOS-only attribute; harmless elsewhere
		label.appendChild(input);
		document.head.appendChild(label);
		label.click();
		document.head.removeChild(label);
	}

	// Fire a short tap. Call this only from within a user gesture (a click /
	// keydown handler), otherwise both mechanisms are no-ops by design.
	function haptic(ms) {
		if (navigator.vibrate) {
			try { navigator.vibrate(ms || 10); } catch (e) {}
		}
		try { iosHaptic(); } catch (e) {}
	}

	// ---- Wheel controls ----------------------------------------------------
	function handleAction(actionName) {
		var view = currentView();
		switch (actionName) {
			case "menu":
				popView();
				break;
			case "select":
				if (view.type === "list" && view.selectedIndex >= 0) {
					view.items[view.selectedIndex].action();
				}
				break;
			case "playpause":
				togglePlayPause();
				break;
			case "prev":
				skipTrack(-1);
				break;
			case "next":
				skipTrack(1);
				break;
			case "scroll-up":
				moveSelection(-1);
				break;
			case "scroll-down":
				moveSelection(1);
				break;
		}
	}

	function moveSelection(delta) {
		var view = currentView();
		if (view.type !== "list" || !view.items.length) return;
		var next = view.selectedIndex + delta;
		if (next < 0) next = 0;
		if (next > view.items.length - 1) next = view.items.length - 1;
		if (next !== view.selectedIndex) {
			view.selectedIndex = next;
			render();
		}
	}

	// Button clicks on the wheel (closest() climbs from any inner <svg>/<path>).
	wheel.addEventListener("click", function (e) {
		var btn = e.target.closest("[data-action]");
		if (btn) { haptic(12); handleAction(btn.getAttribute("data-action")); }
	});

	// Mouse-wheel over the device scrolls the current list.
	device.addEventListener("wheel", function (e) {
		if (currentView().type !== "list") return;
		e.preventDefault();
		haptic(6);
		handleAction(e.deltaY > 0 ? "scroll-down" : "scroll-up");
	}, { passive: false });

	// Rotational drag on the click wheel (authentic scroll gesture).
	var dragAngle = null;
	var dragAccum = 0;
	var STEP_DEG = 28;

	function angleFromCenter(e) {
		var rect = wheel.getBoundingClientRect();
		var cx = rect.left + rect.width / 2;
		var cy = rect.top + rect.height / 2;
		return Math.atan2(e.clientY - cy, e.clientX - cx) * 180 / Math.PI;
	}

	wheel.addEventListener("pointerdown", function (e) {
		// Only the bare ring scrolls. Presses on the labelled buttons or the
		// centre have e.target set to that element, so we bail and let their
		// normal click fire (capturing the pointer here would swallow it).
		if (e.target !== wheel) return;
		dragAngle = angleFromCenter(e);
		dragAccum = 0;
		wheel.setPointerCapture(e.pointerId);
	});

	wheel.addEventListener("pointermove", function (e) {
		if (dragAngle === null) return;
		var a = angleFromCenter(e);
		var diff = a - dragAngle;
		if (diff > 180) diff -= 360;
		if (diff < -180) diff += 360;
		dragAccum += diff;
		dragAngle = a;
		while (Math.abs(dragAccum) >= STEP_DEG) {
			haptic(6); // a tick per step, like a real click wheel
			if (dragAccum > 0) { handleAction("scroll-down"); dragAccum -= STEP_DEG; }
			else { handleAction("scroll-up"); dragAccum += STEP_DEG; }
		}
	});

	function endDrag(e) {
		if (dragAngle === null) return;
		dragAngle = null;
		try { wheel.releasePointerCapture(e.pointerId); } catch (err) {}
	}
	wheel.addEventListener("pointerup", endDrag);
	wheel.addEventListener("pointercancel", endDrag);

	// ---- Keyboard ----------------------------------------------------------
	var KEY_ACTIONS = {
		ArrowUp: "scroll-up",
		ArrowDown: "scroll-down",
		Enter: "select",
		" ": "playpause",
		Backspace: "menu",
		ArrowLeft: "prev",
		ArrowRight: "next"
	};
	document.addEventListener("keydown", function (e) {
		var key = e.key;
		var action = KEY_ACTIONS[key];
		if (!action && (key === "m" || key === "M")) { action = "menu"; }
		if (!action) return;
		var tag = (e.target.tagName || "").toLowerCase();
		if (tag === "input" || tag === "textarea" || e.target.isContentEditable) return;
		e.preventDefault();
		haptic(10);
		handleAction(action);
	});

	// ---- YouTube IFrame API ------------------------------------------------
	window.onYouTubeIframeAPIReady = function () {
		ytPlayer = new YT.Player("ytPlayer", {
			width: 480,
			height: 270,
			playerVars: { playsinline: 1, rel: 0, modestbranding: 1 },
			events: {
				onReady: function () {
					ytReady = true;
					if (pendingYtId) {
						ytPlayer.loadVideoById(pendingYtId);
						ytPlayer.playVideo();
						pendingYtId = null;
					}
				},
				onStateChange: function (e) {
					// 1 = playing, 2 = paused, 0 = ended
					if (e.data === 1) { setPlaying(true); }
					else if (e.data === 2 || e.data === 0) { setPlaying(false); }
					if (e.data === 0) { skipTrack(1); } // auto-advance
				}
			}
		});
	};

	// ---- SoundCloud Widget API ---------------------------------------------
	function initSoundCloud() {
		var iframe = document.getElementById("scWidget");
		if (!iframe || !scUrl || typeof SC === "undefined") return;
		iframe.src = "https://w.soundcloud.com/player/?url=" +
			encodeURIComponent(scUrl) +
			"&color=%232f6fc4&auto_play=false&hide_related=true" +
			"&show_comments=false&show_user=true&show_reposts=false&visual=false";

		scWidget = SC.Widget(iframe);
		scWidget.bind(SC.Widget.Events.READY, function () {
			scWidget.getSounds(function (sounds) {
				// Widget order is newest-first; reverse for ascending display.
				scSounds = sounds.map(function (sound, i) {
					return {
						title: sound.title || ("Track " + (i + 1)),
						description: sound.description || "",
						date: sound.created_at || sound.created || "",
						widgetIndex: i
					};
				}).reverse();
				scReady = true;
				if (currentView().title === "SoundCloud" &&
					currentView().type === "loading") {
					stack[stack.length - 1] = buildSoundCloudList();
					render();
				}
			});
			scWidget.bind(SC.Widget.Events.PLAY, function () { setPlaying(true); });
			scWidget.bind(SC.Widget.Events.PAUSE, function () { setPlaying(false); });
			scWidget.bind(SC.Widget.Events.FINISH, function () { setPlaying(false); });
		});
	}

	if (typeof SC !== "undefined") {
		initSoundCloud();
	} else {
		var tries = 0;
		var scPoll = setInterval(function () {
			tries++;
			if (typeof SC !== "undefined") { clearInterval(scPoll); initSoundCloud(); }
			else if (tries > 40) { clearInterval(scPoll); }
		}, 150);
	}

	// ---- Boot --------------------------------------------------------------
	pushView(buildMainMenu());
	if (device && device.focus) { device.focus(); }
})();
