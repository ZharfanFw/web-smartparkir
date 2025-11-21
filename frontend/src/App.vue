<script setup>
import { ref, onMounted, computed } from 'vue'

// --- 1. KONFIGURASI (SUDAH DIPERBAIKI: TANPA 7B) ---
const floors = ['B', '1A', '1B', '2A', '2B', '3A', '3B', '4A', '4B', '5A', '5B', '6A', '6B', '7A']
const slotsPerFloor = 50
const parkingData = ref({})
const lastLog = ref("Menunggu koneksi server...")

// --- 2. HELPER CLASS WARNA ---
const getStatusClass = (status) => {
  switch (status) {
    case 'GREEN': return 'bg-emerald-500 shadow-[0_0_5px_rgba(16,185,129,0.5)] hover:bg-emerald-400'
    case 'RED': return 'bg-rose-600 scale-110 border-2 border-white z-10 shadow-lg'
    case 'YELLOW': return 'bg-amber-400 text-black animate-pulse border border-yellow-600'
    default: return 'bg-slate-700'
  }
}

// --- 3. INISIALISASI DATA ---
floors.forEach(floor => {
  parkingData.value[floor] = []
  for (let i = 1; i <= slotsPerFloor; i++) {
    const slotId = `${floor}-${i.toString().padStart(2, '0')}`
    parkingData.value[floor].push({ id: slotId, status: 'GREEN' })
  }
})

// --- 4. MAPPING LAYOUT (Computed) ---
const mappedLayout = computed(() => {
  const layout = {}
  for (const floor of floors) {
    const slots = parkingData.value[floor] || [] // Kasih fallback array kosong biar gak error
    if (slots.length === 50) {
      layout[floor] = {
        top_row: slots.slice(0, 10),
        mid_row_top: slots.slice(10, 20),
        mid_row_bottom: slots.slice(20, 30),
        bottom_row: slots.slice(30, 40),
        left_col: slots.slice(40, 45),
        right_col: slots.slice(45, 50),
      }
    }
  }
  return layout
})

// --- 5. KONEKSI WEBSOCKET ---
onMounted(() => {
  const socket = new WebSocket("ws://localhost:8000/ws")

  socket.onopen = () => { lastLog.value = "✅ Terhubung! Simulasi berjalan..." }

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.message) lastLog.value = `[${data.time}] ${data.message}`

      if (data.id && data.status) {
        const [floorName, number] = data.id.split('-')
        if (parkingData.value[floorName]) {
          const slotIndex = parseInt(number) - 1
          if (parkingData.value[floorName][slotIndex]) {
            parkingData.value[floorName][slotIndex].status = data.status
          }
        }
      }
    } catch (e) {
      console.error("Error parsing data:", e)
    }
  }

  socket.onclose = () => { lastLog.value = "❌ Terputus. Pastikan backend jalan!" }
})
</script>

<template>
  <div class="min-h-screen bg-slate-900 text-slate-200 font-sans pb-20 selection:bg-indigo-500">

    <header class="sticky top-0 z-50 bg-slate-900/95 backdrop-blur border-b border-slate-700 shadow-2xl py-4">
      <div class="max-w-7xl mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="bg-indigo-600 p-2 rounded-lg">🅿️</div>
          <h1 class="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-cyan-300 bg-clip-text text-transparent">
            Smart Parking AI</h1>
        </div>
        <div
          class="bg-black/50 border border-slate-700 px-4 py-2 rounded font-mono text-sm text-cyan-400 flex items-center gap-3">
          <span class="relative flex h-3 w-3">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
          </span>
          {{ lastLog }}
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 mt-8 flex flex-col gap-10">
      <div v-for="(layout, floor) in mappedLayout" :key="floor"
        class="bg-slate-800/50 border border-slate-700 rounded-xl p-6 shadow-lg">
        <h2 class="text-xl font-bold text-indigo-300 mb-4 border-b border-slate-700 pb-2">Lantai {{ floor }}</h2>

        <div class="flex flex-col items-center gap-4 bg-slate-900/80 p-4 rounded-lg border border-slate-700">

          <div class="flex gap-2">
            <div v-for="slot in layout.top_row" :key="slot.id"
              class="w-8 h-10 rounded flex items-center justify-center text-xs font-bold transition-all duration-300 cursor-pointer"
              :class="getStatusClass(slot.status)">
              {{ slot.id.split('-')[1] }}
            </div>
          </div>

          <div class="w-full h-1 bg-slate-600 rounded-full"></div>

          <div class="flex justify-between w-full gap-8">
            <div class="flex flex-col gap-2">
              <div v-for="slot in layout.left_col" :key="slot.id"
                class="w-10 h-8 rounded flex items-center justify-center text-xs font-bold transition-all duration-300 cursor-pointer"
                :class="getStatusClass(slot.status)">
                {{ slot.id.split('-')[1] }}
              </div>
            </div>

            <div class="flex flex-col gap-1">
              <div class="flex gap-2">
                <div v-for="slot in layout.mid_row_top" :key="slot.id"
                  class="w-8 h-10 rounded flex items-center justify-center text-xs font-bold transition-all duration-300 cursor-pointer"
                  :class="getStatusClass(slot.status)">
                  {{ slot.id.split('-')[1] }}
                </div>
              </div>
              <div class="flex gap-2">
                <div v-for="slot in layout.mid_row_bottom" :key="slot.id"
                  class="w-8 h-10 rounded flex items-center justify-center text-xs font-bold transition-all duration-300 cursor-pointer"
                  :class="getStatusClass(slot.status)">
                  {{ slot.id.split('-')[1] }}
                </div>
              </div>
            </div>

            <div class="flex flex-col gap-2">
              <div v-for="slot in layout.right_col" :key="slot.id"
                class="w-10 h-8 rounded flex items-center justify-center text-xs font-bold transition-all duration-300 cursor-pointer"
                :class="getStatusClass(slot.status)">
                {{ slot.id.split('-')[1] }}
              </div>
            </div>
          </div>

          <div class="w-full h-1 bg-slate-600 rounded-full"></div>

          <div class="flex gap-2 relative">
            <div v-for="slot in layout.bottom_row" :key="slot.id"
              class="w-8 h-10 rounded flex items-center justify-center text-xs font-bold transition-all duration-300 cursor-pointer"
              :class="getStatusClass(slot.status)">
              {{ slot.id.split('-')[1] }}
            </div>
            <span class="absolute -left-12 top-2 text-xs font-bold text-green-500">MASUK</span>
            <span class="absolute -right-12 top-2 text-xs font-bold text-red-500">KELUAR</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
<!-- <style> -->
<!-- @reference "./style.css"; -->
<!-- /* sesuaikan path */ -->
<!---->
<!-- .slot-h { -->
<!--   @apply w-10 h-10 flex items-center justify-center rounded-md text-sm font-semibold transition-all duration-200; -->
<!-- } -->
<!---->
<!-- .slot-v { -->
<!--   @apply w-10 h-10 flex items-center justify-center rounded-md text-sm font-semibold transition-all duration-200; -->
<!-- } -->
<!-- </style> -->
