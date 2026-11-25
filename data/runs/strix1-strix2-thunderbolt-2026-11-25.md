# strix1 and strix2 Thunderbolt benchmark, 2026-11-25

- Hardware: Two Bosgame M5s, Ryzen AI Max+ 395 and Radeon 8060S per host; 120 GiB GPU limit per host. strix2 ran the client and strix1 ran the RPC worker.
- Both hosts: Omarchy 4.5.0-3 (Arch), kernel 7.2.15-4-omarchy, ROCm 7.2.4, BIOS 3.11, llama.cpp commit `239242322dc24e8c15a458b1beae5064e3358cf8`.
- Link: direct Thunderbolt networking, two negotiated 10 Gb/s lanes in each direction, MTU 1500. Negotiated link rate is distinct from measured application throughput.
- Placement: all model layers offloaded, with equal requested layer split between ROCm and RPC. Each test reports three repeats. The command wall time includes model load and all tests.
- Room temperature and isolated model-load time were not recorded. Power is driver-reported APU socket power; samples began after the first model started loading.

## Qwen3.8 Flash-Next UD-IQ4_XS

Weights: 87.23 GiB. Full command wall time: 186 seconds.

| Prefill tokens | Decode tokens | Initial depth | Median tok/s | Individual repeats (tok/s) |
| ---: | ---: | ---: | ---: | --- |
| 512 | 0 | 0 | 581.70 | 574.40, 583.44, 581.70 |
| 8192 | 0 | 0 | 904.93 | 907.19, 904.93, 894.20 |
| 0 | 128 | 0 | 23.69 | 23.69, 24.31, 23.69 |
| 512 | 0 | 8192 | 496.74 | 496.74, 478.89, 509.79 |
| 8192 | 0 | 8192 | 804.25 | 807.17, 804.25, 800.23 |
| 0 | 128 | 8192 | 22.78 | 22.78, 23.35, 22.67 |

Weights (SHA-256):

```text
93ff23a08e5cd7501f24fa16f5b415d5807d0175e04edd3ed6a7a41b601a4eef  Qwen3.8-Flash-Next-UD-IQ4_XS-00001-of-00004.gguf
13d5dc8b93d039e4cfade5a9af7037f10c97f7ec4e53f75bd2e9ae34aae54aeb  Qwen3.8-Flash-Next-UD-IQ4_XS-00002-of-00004.gguf
f6b9b5934908a2043732269dd740155d0f921d0763a1dcdd3452246311651f87  Qwen3.8-Flash-Next-UD-IQ4_XS-00003-of-00004.gguf
5de8b5dbf89409acc39468decafd4a4a95b13c29d88a14b0356107897829ec36  Qwen3.8-Flash-Next-UD-IQ4_XS-00004-of-00004.gguf
```

Command (substitute the worker address):

```sh
~/.local/src/llama.cpp/build/bin/llama-bench -m ~/models/official/unsloth-Qwen3.8-Flash-Next-UD-IQ4_XS/UD-IQ4_XS/Qwen3.8-Flash-Next-UD-IQ4_XS-00001-of-00004.gguf --rpc <peer-thunderbolt-ip>:50052 -ngl 99 -sm layer -ts 1/1 -r 3 -p 512\,8192 -n 128 -d 0\,8192 -o json --progress
```

## GLM-5.3 Flash UD-IQ2_XXS

Weights: 94.84 GiB. Full command wall time: 389 seconds.

| Prefill tokens | Decode tokens | Initial depth | Median tok/s | Individual repeats (tok/s) |
| ---: | ---: | ---: | ---: | --- |
| 512 | 0 | 0 | 234.85 | 238.87, 234.85, 230.59 |
| 8192 | 0 | 0 | 333.35 | 331.29, 333.35, 333.59 |
| 0 | 128 | 0 | 15.73 | 15.79, 15.72, 15.73 |
| 512 | 0 | 8192 | 168.06 | 167.13, 168.06, 168.12 |
| 8192 | 0 | 8192 | 255.44 | 255.41, 255.44, 255.86 |
| 0 | 128 | 8192 | 14.71 | 14.71, 14.69, 14.71 |

Weights (SHA-256):

```text
337870cefce5fb34b2aa3ade54a0fbf61676697f7f9a906670c20edde74561f4  GLM-5.3-Flash-UD-IQ2_XXS-00001-of-00004.gguf
d51a3d9ca05022d53e71753df75ee64ed5fd4e47655650ae023e9717b3ec158d  GLM-5.3-Flash-UD-IQ2_XXS-00002-of-00004.gguf
89180f13784dc1128586b98adf1ca876279881a20bc4f01747703ce352563372  GLM-5.3-Flash-UD-IQ2_XXS-00003-of-00004.gguf
9e0ef47daa1fdffce3cf2ac1594ce4634d176ad018be6e692729757f38d5fbf6  GLM-5.3-Flash-UD-IQ2_XXS-00004-of-00004.gguf
```

Command (substitute the worker address):

```sh
~/.local/src/llama.cpp/build/bin/llama-bench -m ~/models/official/unsloth-GLM-5.3-Flash-UD-IQ2_XXS/UD-IQ2_XXS/GLM-5.3-Flash-UD-IQ2_XXS-00001-of-00004.gguf --rpc <peer-thunderbolt-ip>:50052 -ngl 99 -sm layer -ts 1/1 -r 3 -p 512\,8192 -n 128 -d 0\,8192 -o json --progress
```

## Observed telemetry

| Host | Median socket W while GPU busy >50% | Peak edge °C | Peak GTT GiB |
| --- | ---: | ---: | ---: |
| strix1 | 119.9 | 96.0 | 47.8 |
| strix2 | 55.1 | 71.0 | 46.6 |
