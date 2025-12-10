// Sample heartbeat data for static deployment
// This is used when the API is not available

export const sampleHeartbeat = {
  beat_number: 0,
  timestamp_utc: "2025-12-10T22:22:40.340191+00:00",
  timestamp_local: "2025-12-10T23:22:40.340204",
  backend_name: "statevector_sampler",
  job_id: "simulator",
  execution_time_seconds: 0.022,
  num_qubits: 5,
  circuit_depth: 8,
  shots: 1024,
  counts: {
    "00000": 897,
    "00100": 18,
    "10000": 55,
    "01000": 37,
    "00010": 10,
    "01100": 2,
    "11000": 3,
    "00001": 2
  },
  coherence_estimate: 0.8759765625,
  entropy: 0.1589065933297454,
  top_states: [
    { state: "00000", count: 897, probability: 0.8759765625 },
    { state: "10000", count: 55, probability: 0.0537109375 },
    { state: "01000", count: 37, probability: 0.0361328125 },
    { state: "00100", count: 18, probability: 0.017578125 },
    { state: "00010", count: 10, probability: 0.009765625 }
  ],
  budget_used_total: 0.022,
  budget_remaining: 599.978
}

// Multiple heartbeats for temporal visualization
export const heartbeatHistory = [
  {
    beat_number: 0,
    coherence_estimate: 0.876,
    entropy: 0.156,
    counts: { "00000": 897, "10000": 55, "01000": 37, "00100": 18, "00010": 10 }
  },
  {
    beat_number: 1,
    coherence_estimate: 0.579,
    entropy: 0.419,
    counts: { "00000": 593, "11111": 215, "10101": 108, "01010": 65, "00110": 43 }
  },
  {
    beat_number: 2,
    coherence_estimate: 0.264,
    entropy: 0.631,
    counts: { "00000": 270, "11111": 198, "10101": 165, "01010": 142, "00110": 129, "11001": 120 }
  }
]
