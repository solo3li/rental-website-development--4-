// Global State and Helpers for Antigravity Rental Website
document.addEventListener("DOMContentLoaded", function () {
  // Initialize Lucide icons
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // Load Saved Favorites from localStorage
  window.updateSavedCount = function () {
    try {
      const saved = JSON.parse(localStorage.getItem("saved_properties_ids") || "[]");
      const countBadges = document.querySelectorAll(".saved-count-badge");
      countBadges.forEach(b => {
        b.textContent = saved.length;
        b.style.display = saved.length > 0 ? "inline-flex" : "none";
      });

      // Update heart button states across all cards
      document.querySelectorAll("[data-save-btn]").forEach(btn => {
        const id = parseInt(btn.getAttribute("data-property-id"));
        const icon = btn.querySelector("svg");
        if (saved.includes(id)) {
          btn.classList.add("text-red-500");
          if (icon) icon.classList.add("fill-red-500", "text-red-500");
        } else {
          btn.classList.remove("text-red-500");
          if (icon) icon.classList.remove("fill-red-500", "text-red-500");
        }
      });
    } catch (e) {
      console.error(e);
    }
  };

  window.toggleSaveProperty = function (id) {
    id = parseInt(id);
    try {
      let saved = JSON.parse(localStorage.getItem("saved_properties_ids") || "[]");
      if (saved.includes(id)) {
        saved = saved.filter(item => item !== id);
      } else {
        saved.push(id);
      }
      localStorage.setItem("saved_properties_ids", JSON.stringify(saved));
      window.updateSavedCount();
      if (window.renderSavedDrawer) {
        window.renderSavedDrawer();
      }
    } catch (e) {
      console.error(e);
    }
  };

  window.updateSavedCount();

  // Modals management
  window.openModal = function (id) {
    const el = document.getElementById(id);
    if (el) {
      el.classList.remove("hidden");
      el.classList.add("flex");
      document.body.style.overflow = "hidden";
      if (window.lucide) window.lucide.createIcons();
    }
  };

  window.closeModal = function (id) {
    const el = document.getElementById(id);
    if (el) {
      el.classList.add("hidden");
      el.classList.remove("flex");
      document.body.style.overflow = "auto";
    }
  };

  window.openPropertyDetailById = function (id) {
    id = parseInt(id);
    if (window.allPropertiesData) {
      const prop = window.allPropertiesData.find(p => p.id === id);
      if (prop) {
        window.openPropertyDetail(prop);
      }
    }
  };

  // Property Detail Modal Populator
  window.openPropertyDetail = function (propertyData) {
    if (typeof propertyData === "string") {
      try { propertyData = JSON.parse(propertyData); } catch (e) {}
    }
    window.currentModalProperty = propertyData;
    const modal = document.getElementById("propertyDetailModal");
    if (!modal) return;

    const isAr = document.documentElement.dir === "rtl";
    const title = (isAr && propertyData.title_ar) ? propertyData.title_ar : propertyData.title;
    const desc = (isAr && propertyData.description_ar) ? propertyData.description_ar : propertyData.description;

    // Safe helper to set text content
    const setElText = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val !== undefined && val !== null ? val : "";
    };

    // Set Text Content
    setElText("modalTitle", title);
    setElText("modalAddress", `${propertyData.address}, ${propertyData.city}, ${propertyData.state} ${propertyData.zip_code}`);
    setElText("modalBeds", `${propertyData.bedrooms} Beds`);
    setElText("modalBaths", `${propertyData.bathrooms} Baths`);
    setElText("modalSqft", `${propertyData.area_sqft} Ft²`);
    setElText("modalBadge", propertyData.badge || "Perfect Fit");
    setElText("modalDesc", desc);

    // Pricing
    const isBuy = propertyData.listing_type === "buy";
    const priceText = isBuy 
      ? `$${(propertyData.buy_price || 150000).toLocaleString()}` 
      : `$${(propertyData.price || 2000).toLocaleString()}`;
    setElText("modalPrice", priceText);
    setElText("modalPriceSuffix", isBuy ? "" : "/mo");

    // Cost Breakdown
    const baseRent = propertyData.price || 2000;
    const secDep = Math.round(baseRent * 1.5);
    const estUtil = 210;
    const totalMove = baseRent + secDep + estUtil;
    setElText("modalBaseRent", `$${baseRent.toLocaleString()}`);
    setElText("modalSecDeposit", `$${secDep.toLocaleString()}`);
    setElText("modalTotalMoveIn", `$${totalMove.toLocaleString()}`);

    // Agent Details
    setElText("modalAgentName", propertyData.agent_name || "Sarah Jenkins");
    setElText("modalAgentPhone", propertyData.agent_phone || "+1 (555) 234-5678");
    setElText("modalAgentEmail", propertyData.agent_email || "agent@horizon.com");
    
    const avatarEl = document.getElementById("modalAgentAvatar");
    if (avatarEl && propertyData.agent_avatar) {
      avatarEl.src = propertyData.agent_avatar;
    }

    const callLink = document.getElementById("modalCallLink");
    if (callLink && propertyData.agent_phone) {
      callLink.href = `tel:${propertyData.agent_phone}`;
    }

    const emailLink = document.getElementById("modalEmailLink");
    if (emailLink && propertyData.agent_email) {
      emailLink.href = `mailto:${propertyData.agent_email}`;
    }

    // Amenities List
    const amenitiesContainer = document.getElementById("modalAmenities");
    if (amenitiesContainer && propertyData.amenities) {
      amenitiesContainer.innerHTML = propertyData.amenities.map(a => `
        <div class="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200/60 text-slate-700 text-xs font-medium">
          <i data-lucide="check" class="w-3.5 h-3.5 text-emerald-600"></i>
          <span>${a}</span>
        </div>
      `).join('');
    }

    // Family Highlights
    const familyContainer = document.getElementById("modalFamilyHighlights");
    if (familyContainer && propertyData.family_highlights && propertyData.family_highlights.length > 0) {
      familyContainer.parentElement.style.display = "block";
      familyContainer.innerHTML = propertyData.family_highlights.map(h => `
        <li class="flex items-start gap-2 text-xs text-slate-600">
          <i data-lucide="sparkles" class="w-3.5 h-3.5 text-amber-500 shrink-0 mt-0.5"></i>
          <span>${h}</span>
        </li>
      `).join('');
    } else if (familyContainer) {
      familyContainer.parentElement.style.display = "none";
    }

    // Photos Gallery
    const images = propertyData.images && propertyData.images.length > 0
      ? propertyData.images
      : ["https://images.pexels.com/photos/8134745/pexels-photo-8134745.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=627&w=1200"];

    const mainPhoto = document.getElementById("modalMainPhoto");
    mainPhoto.src = images[0];

    const thumbsContainer = document.getElementById("modalThumbnails");
    if (thumbsContainer) {
      thumbsContainer.innerHTML = images.map((img, idx) => `
        <button onclick="document.getElementById('modalMainPhoto').src = '${img}'" 
          class="shrink-0 w-20 h-14 rounded-xl overflow-hidden border-2 border-transparent hover:border-blue-500 focus:border-blue-500 transition cursor-pointer">
          <img src="${img}" class="w-full h-full object-cover" />
        </button>
      `).join('');
    }

    // Tour Form hidden property ID
    const tourPropInput = document.getElementById("id_property");
    if (tourPropInput) {
      tourPropInput.value = propertyData.id;
    }

    // Save button state in modal
    const saveBtn = document.getElementById("modalSaveBtn");
    if (saveBtn) {
      saveBtn.setAttribute("data-property-id", propertyData.id);
      saveBtn.onclick = function () {
        window.toggleSaveProperty(propertyData.id);
      };
    }

    window.openModal("propertyDetailModal");
    window.updateSavedCount();
  };

  // Tour Booking Form AJAX & Confetti
  const tourForm = document.getElementById("tourBookingForm");
  if (tourForm) {
    tourForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(tourForm);
      const submitBtn = tourForm.querySelector("button[type='submit']");
      const originalText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = "Booking...";

      fetch("/tours/book/?format=json", {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest"
        }
      })
      .then(res => res.json())
      .then(data => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
        if (data.success) {
          // Trigger Confetti Celebration!
          if (window.confetti) {
            window.confetti({
              particleCount: 120,
              spread: 70,
              origin: { y: 0.6 }
            });
          }
          const successBox = document.getElementById("tourSuccessAlert");
          if (successBox) {
            successBox.classList.remove("hidden");
            setTimeout(() => { successBox.classList.add("hidden"); }, 5000);
          }
          tourForm.reset();
        } else {
          alert("Please fill all required fields properly.");
        }
      })
      .catch(err => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
        console.error(err);
      });
    });
  }

  // Interactive Map Rendering (Matching InteractiveMap.tsx Canvas)
  window.initInteractiveMap = function (properties) {
    const mapContainer = document.getElementById("interactiveMapCanvas");
    if (!mapContainer || !properties || properties.length === 0) return;

    const lats = properties.map(p => parseFloat(p.lat) || 40.7);
    const lngs = properties.map(p => parseFloat(p.lng) || -74.0);

    const minLat = Math.min(...lats, 40.5);
    const maxLat = Math.max(...lats, 43.5);
    const minLng = Math.min(...lngs, -79.0);
    const maxLng = Math.max(...lngs, -73.5);

    const getCoordinates = (latStr, lngStr) => {
      const lat = parseFloat(latStr) || 41.5;
      const lng = parseFloat(lngStr) || -75.0;
      const x = ((lng - minLng) / (maxLng - minLng || 1)) * 75 + 12;
      const y = 88 - ((lat - minLat) / (maxLat - minLat || 1)) * 75;
      return { x: Math.max(10, Math.min(90, x)), y: Math.max(12, Math.min(88, y)) };
    };

    mapContainer.innerHTML = properties.map(p => {
      const coords = getCoordinates(p.lat, p.lng);
      const isBuy = p.listing_type === "buy";
      const priceTag = isBuy ? `$${(p.buy_price || 150000) / 1000}k` : `$${p.price || 2000}`;

      return `
        <div class="absolute cursor-pointer transition-transform duration-200 hover:scale-110 hover:z-30 group"
          style="left: ${coords.x}%; top: ${coords.y}%;"
          onclick='window.openPropertyDetail(${JSON.stringify(p)})'>
          
          <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white text-slate-900 border border-slate-300 shadow-lg font-bold text-xs hover:bg-emerald-600 hover:text-white transition">
            <i data-lucide="map-pin" class="w-3.5 h-3.5 text-emerald-600 group-hover:text-white"></i>
            <span>${priceTag}</span>
          </div>

          <!-- Hover Card Preview -->
          <div class="hidden group-hover:block absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-52 bg-white rounded-2xl p-2 shadow-2xl border border-slate-100 z-40">
            <img src="${p.images[0]}" class="w-full h-24 object-cover rounded-xl mb-1.5" />
            <div class="text-[11px] font-semibold text-slate-800 truncate">${p.title}</div>
            <div class="text-[10px] text-slate-500">${p.city}, ${p.state}</div>
          </div>
        </div>
      `;
    }).join('');

    if (window.lucide) window.lucide.createIcons();
  };

  // Saved Properties Drawer
  window.renderSavedDrawer = function () {
    const container = document.getElementById("savedDrawerList");
    if (!container || !window.allPropertiesData) return;

    try {
      const savedIds = JSON.parse(localStorage.getItem("saved_properties_ids") || "[]");
      const savedList = window.allPropertiesData.filter(p => savedIds.includes(p.id));

      if (savedList.length === 0) {
        container.innerHTML = `
          <div class="text-center py-12 text-slate-400">
            <i data-lucide="heart" class="w-12 h-12 mx-auto mb-3 opacity-30"></i>
            <p class="text-sm">You haven't saved any rental properties yet.</p>
          </div>
        `;
      } else {
        container.innerHTML = savedList.map(p => `
          <div class="flex items-center gap-3 p-3 rounded-2xl border border-slate-200/80 hover:border-slate-300 bg-white transition cursor-pointer"
            onclick='window.openPropertyDetail(${JSON.stringify(p)})'>
            <img src="${p.images[0]}" class="w-16 h-16 rounded-xl object-cover shrink-0" />
            <div class="flex-1 min-w-0">
              <h4 class="text-xs font-semibold text-slate-800 truncate">${p.title}</h4>
              <p class="text-[11px] text-slate-500">${p.city}, ${p.state}</p>
              <div class="text-xs font-bold text-emerald-600 mt-1">$${p.price.toLocaleString()}/mo</div>
            </div>
            <button onclick="event.stopPropagation(); window.toggleSaveProperty(${p.id});" class="p-2 text-red-500 hover:bg-red-50 rounded-xl">
              <i data-lucide="x" class="w-4 h-4"></i>
            </button>
          </div>
        `).join('');
      }
      if (window.lucide) window.lucide.createIcons();
    } catch (e) {
      console.error(e);
    }
  };
});
