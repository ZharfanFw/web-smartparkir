<script setup>
import { ref, onMounted, computed } from 'vue';

// --- 1. CONFIG DATA ---
const floors = ['B', '1A', '1B', '2A', '2B', '3A', '3B', '4A', '4B', '5A', '5B', '6A', '6B', '7A'];
const parkingData = ref({});
const lastLog = ref("Menunggu Server...");
const connectionStatus = ref(false);

// Init Data Kosong
floors.forEach(f => {
  parkingData.value[f] = [];
  for (let i = 1; i <= 70; i++) {
    parkingData.value[f].push({
      id: `${f}-${i.toString().padStart(2, '0')}`,
      status: 'GREEN'
    });
  }
});

// --- 2. LOGIC MAPPING VISUAL ---
const mappedLayout = computed(() => {
  const layout = {};
  for (const f of floors) {
    const s = parkingData.value[f];
    if (s && s.length === 70) {
      layout[f] = {
        // ZONA 1: STRATEGIS (DEKAT PINTU/BAWAH) -> Slot 01-10
        depan: s.slice(0, 10),

        // ZONA 2: TENGAH (Slot 11-30)
        tengah_bawah: s.slice(10, 20),
        tengah_atas: s.slice(20, 30),

        tengah_bawah2: s.slice(30, 40),
        tengah_atas2: s.slice(40, 50),

        // ZONA 3: BELAKANG (Slot 31-40)
        belakang: s.slice(50, 60),

        // ZONA 4: SISA/SAYAP (Slot 41-50)
        sayap_kiri: s.slice(60, 65),
        sayap_kanan: s.slice(65, 70)
      };
    }
  }
  return layout;
});

// --- 3. STYLE HELPER ---
const getSlotColor = (status) => {
  if (status === 'GREEN') return 'bg-emerald-500/90 border-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.4)]';
  if (status === 'YELLOW') return 'bg-yellow-400 border-yellow-200 text-black animate-pulse';
  if (status === 'RED') return 'bg-rose-600 border-white scale-110 shadow-lg z-10';
  return 'bg-slate-700';
};

// --- 4. WEBSOCKET ---
onMounted(() => {
  const ws = new WebSocket("ws://localhost:8000/ws");

  ws.onopen = () => {
    connectionStatus.value = true;
    lastLog.value = "✅ Terhubung ke Sistem AI";
  };

  ws.onmessage = (e) => {
    try {
      const d = JSON.parse(e.data);
      // Update Log
      if (d.message) lastLog.value = `[${d.time}] ${d.message}`;

      // Update Status Slot
      if (d.id) {
        const [floor, num] = d.id.split('-');
        const idx = parseInt(num) - 1;
        if (parkingData.value[floor] && parkingData.value[floor][idx]) {
          parkingData.value[floor][idx].status = d.status;
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  ws.onclose = () => {
    connectionStatus.value = false;
    lastLog.value = "❌ Koneksi Terputus";
  };
});
</script>

<template>
  <div class="min-h-screen bg-[#0f172a] text-slate-200 font-sans pb-20">

    <!-- HEADER -->
    <div class="sticky top-0 z-50 bg-[#0f172a]/95 backdrop-blur border-b border-slate-800 shadow-2xl">
      <div class="max-w-7xl mx-auto px-4 py-3 flex flex-col md:flex-row justify-between items-center gap-4">
        <div class="flex items-center gap-3">
          <div
            class="h-10 w-10 bg-indigo-600 rounded-lg flex items-center justify-center shadow-lg shadow-indigo-500/20 font-bold text-xl">
            🅿️</div>
          <div>
            <h1 class="text-xl font-bold text-white tracking-tight">Smart Parking AI</h1>
            <p class="text-xs text-slate-400 font-mono uppercase tracking-wider">Real-time Optimization System</p>
          </div>
        </div>

        <!-- LOG BOX -->
        <div class="flex items-center gap-3 bg-slate-900/50 px-4 py-2 rounded-full border border-slate-700">
          <div class="relative flex h-2.5 w-2.5">
            <span v-if="connectionStatus"
              class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5"
              :class="connectionStatus ? 'bg-green-500' : 'bg-red-500'"></span>
          </div>
          <span class="font-mono text-xs text-cyan-400 truncate max-w-[250px]">{{ lastLog }}</span>
        </div>
      </div>
    </div>

    <!-- CONTENT GRID -->
    <main class="max-w-7xl mx-auto px-4 mt-8 grid gap-8">

      <!-- LOOPING LANTAI -->
      <div v-for="(layout, floor) in mappedLayout" :key="floor"
        class="bg-[#1e293b]/50 border border-slate-700/50 rounded-2xl p-6 relative overflow-hidden">

        <!-- Label Lantai Background -->
        <div class="absolute -right-4 -top-4 text-9xl font-black text-white/[0.03] pointer-events-none select-none">
          {{ floor }}
        </div>

        <div class="relative z-10 flex flex-col items-center">
          <h2
            class="text-lg font-bold text-indigo-300 mb-6 flex items-center gap-2 w-full border-b border-slate-700 pb-2">
            <span class="block w-1.5 h-6 bg-indigo-500 rounded-full"></span>
            Lantai {{ floor }}
          </h2>

          <!-- DENAH PARKIR -->
          <div class="flex flex-col gap-3 bg-[#0f172a] p-5 rounded-xl border border-slate-800 shadow-inner">

            <!-- 1. AREA BELAKANG (Slot 31-40) - Paling Atas -->
            <div class="flex justify-center gap-2">
              <div v-for="s in layout.belakang" :key="s.id" :class="getSlotColor(s.status)"
                class="w-8 h-10 rounded flex items-center justify-center text-[10px] font-bold border border-white/10 transition-all duration-300">
                {{ s.id.split('-')[1] }}
              </div>
            </div>

            <!-- 2. AREA TENGAH (Slot 11-30 + Sayap) -->
            <div class="flex gap-6 justify-center items-center">
              <!-- Sayap Kiri (41-45) -->
              <div class="flex flex-col gap-2">
                <div v-for="s in layout.sayap_kiri" :key="s.id" :class="getSlotColor(s.status)"
                  class="w-10 h-8 rounded flex items-center justify-center text-[10px] font-bold border border-white/10 transition-all duration-300">
                  {{ s.id.split('-')[1] }}
                </div>
              </div>

              <div class="flex flex-col gap-8 mt-4">
                <!-- Blok Tengah -->
                <div class="flex flex-col gap-1">
                  <!-- Tengah Atas (21-30) -->
                  <div class="flex gap-2">
                    <div v-for="s in layout.tengah_atas2" :key="s.id" :class="getSlotColor(s.status)"
                      class="w-8 h-10 rounded flex items-center justify-center text-[10px] font-bold border border-white/10 transition-all duration-300">
                      {{ s.id.split('-')[1] }}
                    </div>
                  </div>
                  <!-- Tengah Bawah (11-20) -->
                  <div class="flex gap-2">
                    <div v-for="s in layout.tengah_bawah2" :key="s.id" :class="getSlotColor(s.status)"
                      class="w-8 h-10 rounded flex items-center justify-center text-[10px] font-bold border border-white/10 transition-all duration-300">
                      {{ s.id.split('-')[1] }}
                    </div>
                  </div>
                </div>

                <div class="flex flex-col gap-1">
                  <!-- Tengah Atas (21-30) -->
                  <div class="flex gap-2">
                    <div v-for="s in layout.tengah_atas" :key="s.id" :class="getSlotColor(s.status)"
                      class="w-8 h-10 rounded flex items-center justify-center text-[10px] font-bold border border-white/10 transition-all duration-300">
                      {{ s.id.split('-')[1] }}
                    </div>
                  </div>
                  <!-- Tengah Bawah (11-20) -->
                  <div class="flex gap-2">
                    <div v-for="s in layout.tengah_bawah" :key="s.id" :class="getSlotColor(s.status)"
                      class="w-8 h-10 rounded flex items-center justify-center text-[10px] font-bold border border-white/10 transition-all duration-300">
                      {{ s.id.split('-')[1] }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- Sayap Kanan (46-50) -->
              <div class="flex flex-col gap-2">
                <div v-for="s in layout.sayap_kanan" :key="s.id" :class="getSlotColor(s.status)"
                  class="w-10 h-8 rounded flex items-center justify-center text-[10px] font-bold border border-white/10 transition-all duration-300">
                  {{ s.id.split('-')[1] }}
                </div>
              </div>
            </div>

            <!-- SPASI SEBELUM AREA DEPAN -->
            <div class="h-2"></div>

            <!-- 3. AREA DEPAN / PINTU (Slot 01-10) - DIPINDAH KE ATAS JALAN -->
            <div class="flex justify-center gap-2 relative p-1">

              <!-- Label Masuk -->
              <div class="absolute -left-14 top-1/2 -translate-y-1/2 flex flex-col items-end gap-1">
                <span
                  class="text-[9px] font-bold text-emerald-400 bg-emerald-900/30 px-1.5 py-0.5 rounded animate-pulse border border-emerald-500/30">MASUK
                  ⬆</span>
              </div>

              <div v-for="s in layout.depan" :key="s.id" :class="getSlotColor(s.status)"
                class="w-8 h-10 rounded flex items-center justify-center text-[10px] font-bold border border-white/10 transition-all duration-300 shadow-lg">
                {{ s.id.split('-')[1] }}
              </div>

              <!-- Label Keluar -->
              <div class="absolute -right-14 top-1/2 -translate-y-1/2 flex flex-col items-start gap-1">
                <span
                  class="text-[9px] font-bold text-rose-400 bg-rose-900/30 px-1.5 py-0.5 rounded border border-rose-500/30">KELUAR
                  ⬇</span>
              </div>
            </div>

            <!-- JALUR UTAMA (Main Road) - DIPINDAH KE PALING BAWAH -->
            <div
              class="w-full h-10 border-t-2 border-dashed border-slate-600/40 relative mt-1 bg-slate-800/20 rounded-b-lg">
              <div class="absolute inset-0 flex items-center justify-center">
                <span class="text-[10px] font-mono text-slate-500 tracking-[0.3em]">JALUR UTAMA</span>
              </div>
            </div>

          </div>
        </div>
      </div>
    </main>
  </div>
</template>
