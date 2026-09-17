# Ziqing Guo — Research Bibliography (compiled 2026-09-16)

**Author identity.** Ziqing Guo (ORCID 0009-0006-3999-2221; GitHub `gzquse`; email ziqguo@ttu.edu). Department of Computer Science, Texas Tech University (TTU), Lubbock, TX; also affiliated with NERSC, Lawrence Berkeley National Laboratory (LBNL). GitHub bio: "I like to develop the new ideas in Quantum Computing / Quantum Cryptography." Advisor / corresponding author on all TTU papers: **Ziwen Pan** (TTU CS). Recurrent coauthors: **Jan Balewski** (NERSC/LBNL), **Alex Khan** (National Quantum Laboratory, Univ. of Maryland; later BosonQ Psi Corp), **Wenshuo Hu** (TTU Chemical Engineering), **Victor S. Sheng** (TTU CS), **Steven Rayan** (Univ. of Saskatchewan), **Kewen Xiao** (RIT), **Jie Li**, **Yong Chen** (TTU), and industry coauthors at Lightrider (Anthony Lawrence, Renyu Wang), Quantropi (Randy Kuang) and BosonQ Psi (Viraj Dsouza, Abhishek Chopra, Rut Lineswala).

**Sources used.** DataCite API (arXiv + Zenodo DOIs registered to "Guo, Ziqing"), Crossref API (published versions), arXiv full-text HTML pages of every paper, GitHub API/repo pages, Semantic Scholar (partial; heavily rate-limited), Research Square, AAAI OJS, nature.com. Google Scholar, dblp, ORCID and ResearchGate were not reachable from this environment.

**Disambiguation.** There are several unrelated researchers named Ziqing Guo (KU Leuven electromagnetics/PINN; Dalian process-systems engineering; a biostatistician; a biomedical NLP author). Only the quantum/HPC/ML/crypto works with TTU/NERSC affiliation and Pan/Balewski coauthorship are listed as confirmed. One 2018 blockchain/IoT cryptography paper is listed separately as "possibly the same person".

---

## Part 1. Confirmed publications (chronological by first appearance)

### 1. Q-GEAR: Improving quantum simulation framework
- **Authors:** Ziqing Guo, Jan Balewski, Ziwen Pan (arXiv/DataCite creator order lists Guo, Pan, Balewski; the paper header and the ACM record list Guo, Balewski, Pan)
- **Year:** 2025 (arXiv v1: 4 Apr 2025)
- **Venue / status:** Published, ACM ICPP 2025 (54th International Conference on Parallel Processing, San Diego, CA, Sept 2025). ACM registered **two** DOIs: main proceedings pp. 638–647, DOI 10.1145/3754598.3754608, and Workshop Proceedings pp. 200–209, DOI 10.1145/3750720.3757302 (indexed 20 Dec 2025). *Which one is canonical is unclear — likely a workshop paper that was also included in the main volume; verify with ACM DL.*
- **arXiv:** 2504.03967 (quant-ph) — https://arxiv.org/abs/2504.03967
- **GitHub:** https://github.com/gzquse/qgear (Apache-2.0, ~7 stars, 241 commits; nbdev-based Python package) ; related fork https://github.com/gzquse/cudaq-perlmutter (from zohimchandani/cudaq-perlmutter, "Executing CUDA-Q on multiple nodes on Perlmutter")
- **Funding:** DOE Office of Science, NERSC award DDR-ERCAP0034486.
- **Summary:** Q-Gear is a software framework that automatically transforms Qiskit circuits (currently H, RY, RZ, U3, CX, CP, SWAP and measurement) into CUDA-Q kernels so that the same circuit can be executed on NVIDIA GPUs without rewriting, and it packages the whole stack as Podman/Shifter containers optimized for Slurm on Perlmutter (NERSC). Relative to CPU state-vector simulation (2× AMD EPYC 7763, 128 cores, 512 GB) the GPU path is roughly two orders of magnitude faster (a ~400× speed-up on a single A100 is reported), and relative to existing GPU simulators (Qiskit Aer GPU, PennyLane Lightning) it is about 10× faster with minimal coding effort. Using CUDA-Q's multi-GPU/MPI memory interconnect, a 34-qubit random unitary ran in about 1 minute on 4 A100s versus ~24 hours on CPU, 32 qubits fit on one 40 GB A100, and circuits up to **42 qubits** were simulated on up to **1,024 A100 GPUs** with close to 100% GPU utilization. Benchmarks include random CX-block circuits with 100–10,000 two-qubit gates (28–34 qubits), QFT up to 22 qubits, and QCrank quantum image encoding circuits (speed-ups approaching two orders of magnitude for small images). Appendices cover state-vector simulation, circuit encoding, HDF5 data management, the pipeline configuration and QCrank benchmark details.
- **Thesis theme:** **(A)** HPC large-scale circuit simulation (also supports C via QCrank image encoding).

### 2. Quantum parallel information exchange (QPIE) hybrid network with transfer learning
- **Authors:** Ziqing Guo, Alex Khan, Victor S. Sheng, Shabnam Jabeen, Ziwen Pan
- **Affiliations:** TTU (Guo, Sheng, Pan); National Quantum Laboratory, Maryland (Khan); University of Maryland (Jabeen)
- **Year:** 2025 (arXiv v1: 5 Apr 2025; journal 3 Jul 2025)
- **Venue / status:** Published, *Quantum Science and Technology* (IOP), vol. 10 (2025), DOI 10.1088/2058-9565/ade89f (article number not retrieved — TODO). Semantic Scholar citation count: 4 (Sept 2026).
- **arXiv:** 2504.04235 — https://arxiv.org/abs/2504.04235
- **GitHub:** https://github.com/gzquse/QPIE_datacircuit (Jupyter/Python; Dockerfile.pennylane; PyTorch 24.06 Shifter container; requires NVIDIA A100 80 GB)
- **Acknowledgements:** Xanadu (AWS Braket credits for IonQ hardware); TTU HPCC.
- **Summary:** QPIE is a *non-sequential* hybrid classical–quantum architecture: pretrained classical network parameters are fed in parallel into variational quantum circuits built from non-Clifford parameterized gates, with information exchanged between the classical and quantum branches rather than stacked sequentially (quantum transfer learning). A dynamic gradient-selection scheme uses the parameter-shift rule when running on QPUs and adjoint differentiation when simulating on GPUs, and the model is evaluated on Moon/Spiral toy sets, Hymenoptera, Brain-Tumor MRI, MNIST, and NARMA5/NARMA10 time series. Reported accuracies are 0.95–0.99 (Moon), 0.96–0.99 (Spiral), 0.87–0.91 (Brain Tumor) and 0.93–0.97 (MNIST) versus 0.93/0.90/0.76/0.81 for the classical baseline; convergence on stochastic time series is ~88% faster within 100 steps; GPU simulators give up to 30× speed-up; and the Fisher-information spectrum is less biased (eigenvalues up to ~16 versus ~7 for classical transfer learning). Circuits used up to 28 qubits (10 data + 2 ancilla per block) on Amazon Braket SV1, IonQ Aria-1 and local A100 simulators.
- **Thesis theme:** **(C)** quantum machine learning / encoding.

### 3. Direct Entanglement Ansatz Learning (DEAL) with ZNE on Error-Prone Superconducting Qubits
- **Authors:** Ziqing Guo, Steven Rayan, Wenshuo Hu, Ziwen Pan
- **Affiliations:** TTU (Guo, Hu, Pan); University of Saskatchewan, Saskatoon (Rayan)
- **Year:** 2025 (arXiv v1: 5 Apr 2025; conference Aug 31–Sep 5, 2025)
- **Venue / status:** Published, *2025 IEEE International Conference on Quantum Computing and Engineering (QCE)*, Albuquerque, NM, pp. 320–325, DOI 10.1109/QCE65121.2025.10343.
- **arXiv:** 2504.04021 — https://arxiv.org/abs/2504.04021
- **GitHub:** https://github.com/gzquse/DEAL_QUBO (Python; 53 commits; `pl_sum.py`, `launch.sh` distributed training, D-Wave Leap MVRP annealing scripts, Qiskit GPU kernel, IBM job submission/tracking)
- **Acknowledgements:** TTU HPCC.
- **Summary:** DEAL replaces the black-box optimization of QAOA angles with a *direct mapping* from QUBO problem coefficients to the cost- and mixer-Hamiltonian ansatz angles, combined with an entanglement-based ansatz (echoed cross-resonance gates for maximal entanglement) and an adaptive digital zero-noise extrapolation (ZNE) that inserts delay/identity gates to control crosstalk and coherence errors. Experiments on IBM Torino (133 qubits) and IBM Marrakesh (156 qubits) with 20-qubit, 10-layer circuits show up to **14% higher success rate** in reaching the ground-state energy than vanilla QAOA (14.81% on Torino, 7.40% on Marrakesh at layer 10) and lower error variance; DEAL reaches with 7 layers what QAOA needs 9 layers for, with performance degrading beyond ~41–43 CZ gates. It provides near-optimal ground energies for travelling-salesman, knapsack and MaxCut instances (Table II optima 8.795/7.468, 39.167, 14.184) and introduces a Quantum Noise-Limited Relative Error (QNRE) metric and Bayesian-optimization-based layer selection.
- **Thesis theme:** **(B)** QAOA / optimization / NISQ error mitigation.

### 4. Vectorized Attention with Learnable Encoding for Quantum Transformer (VQT)
- **Authors:** Ziqing Guo, Ziwen Pan, Alex Khan, Jan Balewski
- **Affiliations:** TTU + NERSC/LBNL (Guo); TTU (Pan); National Quantum Laboratory, MD (Khan); NERSC/LBNL (Balewski)
- **Year:** 2025 (arXiv v1: 25 Aug 2025; proceedings 23 Nov 2025)
- **Venue / status:** Published, *Proceedings of the AAAI Symposium Series*, vol. 7, no. 1, pp. 350–357 (AAAI Fall Symposium Series 2025, First AAAI Symposium on Quantum Information & Machine Learning (QIML)), DOI 10.1609/aaaiss.v7i1.36905.
- **arXiv:** 2508.18464 — https://arxiv.org/abs/2508.18464
- **GitHub:** https://github.com/gzquse/quantum-transformer (Python; dirs `datacircuits`, `exploratory`, `paper_AAAI2025`, `stable`, `toolbox`; IonQ API job scripts) and https://github.com/gzquse/paper_AAAI2025-quantum (figure-reproduction scripts `figB_resIdeal.py`, `figC_resHW.py`, `data/`, `data_ionq/`); Mathematica derivations in https://github.com/gzquse/vectorized_encoding (`quantum_arithmatic_V5.nb`).
- **Funding:** DOE/NERSC awards DDR-ERCAP0034486 and DDR-ERCAP0034385; UMD QLab.
- **Summary:** VQT replaces classical self-attention with two shot-efficient, gradient-free quantum primitives built on QCrank-style vectorized block encoding: a Vectorized Quantum Dot Product (VQDP) that estimates the masked attention matrix by quantum approximate simulation, and a Vectorized Nonlinear Quantum Encoder (VNQE) that makes the encoding learnable with a tanh projection head and an "expressive quantum head". The VQDP has complexity O(log(BT²)·shots) versus O(BT²d) classically, and the quantum-vs-classical attention error stays below 1.2% with 3.0 M shots. Hardware runs used 4–9 qubits, batches 4–128, 10K–320K shots and CNOT depth 5–129, giving RMSE 0.059 on IBM Kingston, 0.155 on IonQ Aria-1 and 0.017 on the ideal simulator (batch 32). On Brown-corpus language modelling VQT (6 qubits) reaches quantum perplexity 105.4 / loss 1.12 versus 92.5/0.94 for a 125K-parameter nanoGPT, and beats Q-LSTM (125.3), Quixer (117.1) and a hybrid QT (127.6). A variance proof for VQDP is given in the appendix.
- **Thesis theme:** **(C)** quantum ML / transformer / encoding.

### 5. Quantum Data Representation via Circuit Partitioning and Reintegration (ShardQ)
- **Authors:** Ziqing Guo, Jan Balewski, Kewen Xiao, Ziwen Pan
- **Affiliations:** TTU + NERSC/LBNL (Guo); NERSC/LBNL (Balewski); Rochester Institute of Technology (Xiao); TTU (Pan)
- **Year:** 2025 (arXiv v1: 7 Nov 2025)
- **Venue / status:** arXiv preprint (no published version found as of Sept 2026).
- **arXiv:** 2511.05492 — https://arxiv.org/abs/2511.05492
- **GitHub:** https://github.com/gzquse/ShardQ_v2 (Python, MIT; SparseCut, hardware-aware cut finding using calibration data, MPS simulation to 100+ qubits, comparisons vs CutQC/random cuts; depends on qiskit-addon-cutting); theorems supported by `common_decompose.nb` in gzquse/vectorized_encoding.
- **Funding:** DOE/NERSC DDR-ERCAP0034486.
- **Summary:** ShardQ is a hardware-aware circuit cutting-and-knitting framework for quantum data-encoding circuits (QCrank-type uniformly controlled rotations). A deterministic **SparseCut** algorithm (O(|G| log |G|)) chooses gate cuts based on physical qubit distance and calibrated error rates, sub-circuits are compiled with a matrix-product-state (MPS) approximate compiler of bounded bond dimension, and outputs are recombined by a global (rather than pairwise) quasi-probability reconstruction. On IBM Heron-3 (ibm_pittsburgh; median CZ error 1.46e-3) and Heron-2 (ibm_marrakesh) the method reduces RMSE by roughly **15%** relative to standard transpilation, raising the reconstructed-value fidelity of image encodings from 0.79 (QCrank) to 0.90 and from 0.75 to 0.88 as address qubits grow from 5 to 7. Experiments used 2–9 address and 2–8 data qubits, 1,000-pixel images (9 address + 2 data qubits), 1.5 M shots per sub-circuit, and A100 GPUs (one 80 GB GPU for ≤2 cuts, ~15 s; 4 GPU nodes for 4 cuts, ~24 h; QPD overhead O(3^{2k})).
- **Thesis theme:** **(C)** quantum data encoding / **(A)** HPC-assisted (circuit knitting on GPUs); also relevant to NISQ error reduction (B).

### 6. Quantum Approximate Walk Algorithm (QAWA)
- **Authors:** Ziqing Guo, Jan Balewski, Wenshuo Hu, Alex Khan, Ziwen Pan
- **Affiliations:** TTU CS + NERSC/LBNL (Guo); NERSC/LBNL (Balewski); TTU Chemical Engineering (Hu); UMD National Quantum Laboratory (Khan); TTU CS (Pan)
- **Year:** 2025 (arXiv v1: 10 Nov 2025)
- **Venue / status:** arXiv preprint (code "available upon publication" — suggests journal submission; no published version found).
- **arXiv:** 2511.07676 — https://arxiv.org/abs/2511.07676
- **GitHub:** https://github.com/gzquse/qawa_data_circ (Python; `QAWA_v2.py`, `postproc_qawa.py`, `plt_sum.py`; Qiskit 2.2 + Aer HPC backend)
- **Funding:** DOE/NERSC DDR-ERCAP0034486; TTU HPCC.
- **Summary:** QAWA proposes a *classical-data-traceable* quantum oracle whose circuit depth grows linearly with qubit count (O(n) CNOTs versus O(n²) for tomography) so that a shallow quantum circuit can learn approximate solution patterns for QUBO/portfolio problems, and shows that classical preprocessing of mid-circuit measurement data makes QAOA outputs interpretable without full state tomography (O(n²) measurements for n-qubit correlations). A "distributed approximate walk learning" scheme learns copulas: all six pairwise correlation coefficients of a 4-asset S&P 500 portfolio (AAPL, MSFT, JNJ, XOM) were recovered, with KL-divergence converging to 0.01 in ~75 iterations. On IBM Pittsburgh (156-qubit Heron) with 8,192 shots × 20 runs the method gave a 5.4% average improvement over the baseline portfolio and an 8.1% advantage above the noise floor, out-performing QAOA without extra optimization iterations; simulations extend to 20 qubits, and solution quality is verifiable in polynomial time.
- **Thesis theme:** **(B)** QAOA / optimization / NISQ (with encoding ideas from C).

### 7. NNQA: Neural-Native Quantum Arithmetic for End-to-End Polynomial Synthesis
- **Authors:** Ziqing Guo, Jie Li, Yong Chen, Ziwen Pan
- **Affiliations:** LBNL + TTU (Guo); TTU (Li, Chen, Pan)
- **Year:** 2026 (arXiv v1: 28 Mar 2026; preprint dated 31 Mar 2026)
- **Venue / status:** arXiv preprint; formatted as an ML-conference submission (accessibility statement, anonymous repo) — venue TODO.
- **arXiv:** 2603.27297 — https://arxiv.org/abs/2603.27297
- **GitHub:** https://github.com/gzquse/nnqa (Python, MIT; `nnqa/`, `qc/`, `cloud_job/`, `research/`; supports IBM Heron ibm_boston/pittsburgh/fez/marrakesh/kingston/torino and Nighthawk ibm_miami); anonymous mirror https://github.com/tankizgif/NNQA
- **Summary:** NNQA compiles a classically trained polynomial neural network directly into exact quantum arithmetic composed of native unitary blocks (weighted sums and multiplications on real-valued encoded states, in the spirit of EHands/QCrank), avoiding the communication overhead and approximation error of generic variational ansatzes. The paper proves an NNQA universal-approximation theorem and gives a resource model: a degree-6 polynomial needs 7 qubits, 5 CNOTs, depth 19 and a single execution (4,096 shots), versus 6–12 qubits, depth 20–100 and 10²–10³ executions for VQE, or ~10–100 qubits and depth 50 for QSP. On IBM Heron-3 (ibm_boston, 156 qubits), IBM Nighthawk (ibm_miami) and IonQ Forte-1 it reaches >99.5% accuracy for polynomials up to degree 35 (36 qubits, depth 70 in the IonQ stress test), with RMSE ≈ 0.005 on IonQ, RMSE ≤ 0.017 and correlation > 0.999 for degrees 1–30, and hardware pass rates of 74–86% (Heron-3) and 92–99% (Forte-1). Classical training used Perlmutter A100 nodes.
- **Thesis theme:** **(C)** quantum ML / arithmetic encoding (also F: quantum arithmetic/compilation).

### 8. RubriQ: Rubric-Guided Group Relative Policy Optimization for Constraint-Aware Quantum Circuit Synthesis
- **Authors:** Ziqing Guo, Ziwen Pan (TTU CS)
- **Year:** 2026 (arXiv v1: 8 Jul 2026; Research Square preprint 3 Aug 2026)
- **Venue / status:** arXiv preprint; posted on Research Square (DOI 10.21203/rs.3.rs-10309063/v1) as **under review at *npj Quantum Information***. The GitHub artifact is labelled "SC25 Reproducibility Artifact" (the SC submission outcome is unknown — TODO). Software archived on Zenodo, DOI 10.5281/zenodo.21284556 (concept) / 10.5281/zenodo.21284557 (v1), CC-BY-4.0.
- **arXiv:** 2607.07554 — https://arxiv.org/abs/2607.07554
- **GitHub:** https://github.com/gzquse/rubriq-artifact (Python; conda + PyTorch CUDA 12.1; 21 evaluator integration tests; GRPO training on 1–2 A100-80GB nodes, ~200 GB weights); also https://github.com/gzquse/llm_cookbook (LLM utilities, Apr 2026).
- **Summary:** RubriQ frames fault-tolerant circuit synthesis as LLM code generation fine-tuned with Group Relative Policy Optimization (GRPO), where the reward is a *programmatic, domain-grounded rubric* (weights: fidelity 0.40, Clifford correctness 0.20, hardware-topology compliance 0.15, T-gate count 0.15, efficiency 0.10) evaluated with GPU-accelerated CUDA-Q simulation inside the RL loop. Training runs on NERSC Perlmutter with DeepSpeed ZeRO-2 over 4–8 A100 nodes (85% strong-scaling efficiency on 8 GPUs; Slingshot interconnect tuning), using a 7B instruction-tuned coder with LoRA (rank 64, ~28 M trainable parameters), group size N = 8, temperature 0.8, top-p 0.95; the artifact fine-tunes Qwen2.5-Coder variants, DeepSeek-Coder-V2-Lite, Llama-3.1-8B and StarCoder2-15B. On 1,500 benchmark circuits (QFT, QPE, Hamiltonian simulation, data encoding) it achieves **3.31× mean T-gate compression** versus 2.05× for sparse-reward RL, converges 2–3× faster with 2–3× fewer simulator calls, keeps hardware-constraint violations below 1% (5× fewer than the strongest baseline), and reports 96% correctness; multi-strategy parsing recovers ~60% of initially unparseable generations. Synthesized circuits were validated on IBM Heron-3 (156 qubits) and IonQ Forte (36 qubits).
- **Thesis theme:** **(F)** LLM/RL-driven circuit synthesis for FTQC, with strong **(A)** HPC component; touches (D) via T-count/FTQC cost.

### 9. Measurement and reload costs in direct quantum simulation of nonlinear waves
- **Authors:** Ziqing Guo, Viraj Dsouza, Alex Khan, Abhishek Chopra, Rut Lineswala, Ziwen Pan
- **Affiliations:** TTU (Guo, Pan); BosonQ Psi Corp, Syracuse, NY (Dsouza, Khan, Chopra, Lineswala)
- **Year:** 2026 (arXiv v1: 21 Aug 2026; Zenodo code 7 Jul 2026)
- **Venue / status:** arXiv preprint. Code/data archived as "SplitStepQUDE", Zenodo DOI 10.5281/zenodo.21245905 (concept) / 10.5281/zenodo.21245906 (v1), CC-BY-4.0 / Apache-2.0.
- **arXiv:** 2608.21647 — https://arxiv.org/abs/2608.21647
- **GitHub:** repository name not confirmed (Zenodo record "SplitStepQUDE: code and data …"; IBM job path submits executable quantum kernels) — TODO.
- **Summary:** The paper asks what it really costs to simulate nonlinear wave equations (the nonlinear Schrödinger equation and the 1D/2D viscous Burgers equation) on a quantum processor when the nonlinearity needs the field values themselves. Instead of hiding that cost inside Carleman/linear embeddings and state copies, it proposes a hybrid Strang split-step solver in which the field (N = 2^n grid points on n qubits) is measured in the computational basis, updated classically with a degree-d polynomial (O(Nd)), and reloaded by a vectorized QCrank-style loader (Θ(N) CNOTs, ~1.6 µs reload latency at N = 32) at every step, with all shots S and gates accounted for in a single cost-and-error model (shot variance p(1-p)/S, truncation error θ^{d+1}/(d+1)!, norm-defect threshold 0.02). A controller adapts Δt, d ∈ {2,4,6} and S to keep the nonlinear phase per step θ = κ|ψ|²Δt below unity (example κ = 50, T = 0.48, fidelity ≈ 0.95). The coherent kernels (QFT propagator with n(n-1)/2 two-qubit gates, boundary kernels) are validated on an IBM Heron superconducting processor. The main conclusion is negative but quantitative: because every step reads the full field, the quantum cost per step (depth × shots) exceeds the classical cost as N grows, so a coherent, measurement-free nonlinear update is the target any end-to-end advantage must meet.
- **Thesis theme:** **(F)** quantum scientific computing / PDE simulation (uses encoding from C).

### 10. Auditing Structured Randomness for Quantum Error Correction under a Bounded Cloud Fault Model
- **Authors:** Ziqing Guo, Anthony Lawrence, Renyu Wang, Randy Kuang, Ziwen Pan
- **Affiliations:** TTU (Guo, Pan); Lightrider (Lawrence, Wang); Quantropi (Kuang)
- **Year:** 2026 (arXiv v1: 27 Aug 2026)
- **Venue / status:** arXiv preprint; artifact hosted on anonymous.4open.science under the name `usenix_qec_hse`, and the appendices follow a USENIX-style open-science/ethics checklist — likely submitted to a USENIX security venue (TODO).
- **arXiv:** 2608.26600 — https://arxiv.org/abs/2608.26600
- **GitHub / code:** https://anonymous.4open.science/r/usenix_qec_hse-32FE (containerized, seeded, deterministic); related exploratory repos gzquse/ExploreQEC_mar (Apache-2.0; Stim, Qiskit, Guppy, Squin toolboxes; Steane-code cloud simulations for IBM/IQM/Quantinuum; folders `2026LDRD`, `2026QTML`), forks of Stim, tqec, BivariateBicycleCodes.
- **Summary:** The paper studies a security threat to QEC on cloud QPUs: a fixed, public encoder circuit gives a co-located fault-injection adversary a reusable target, whereas per-run *reseeding* of the encoder changes the physical-to-logical fault map. It defines **accepted logical disturbance**, an acceptance-weighted measure of harmful logical action that survives syndrome-based rejection, derives its exact Haar-random expectation, and introduces a polynomial-cost seeded Clifford "Hadamard-structured ensemble" (HSE: Hadamard, phase, permutation and CNOT layers of depth d) as a cheap substitute for exponentially costly Haar encoders. Using the [[5,1,3]] code with weight-one Pauli faults (all 3n faults enumerated), reseeding reduces mean accepted logical disturbance from 0.150 (adversary chooses the fault after learning each encoder) to 0.020 (fault fixed before the seed is known), an 86.7% reduction attributable to rejection; 18.5% of sampled HSE encoders satisfy the exact QEC conditions. Gate-level Stim simulations at n = 17 with depolarizing rates p1 = 1e-3, p2 = 1e-2 confirm the scaling, and the paper places the audit in the context of FIPS 140-3, FIPS 203/204/205 and SP 800-90A randomness standards.
- **Thesis theme:** **(D)** QEC and **(E)** cryptography/security (fault-injection threat model, standards).

### 11. Light Rider Inc. QPC SDK (software release)
- **Creator:** Ziqing Guo (Texas Tech University)
- **Year:** 2026 (Zenodo, 12 Aug 2026), v1.0.0, Linux x86_64, 1.1 MB
- **DOI:** 10.5281/zenodo.21895102 (concept) / 10.5281/zenodo.21895103 (v1); CC-BY-4.0
- **Description:** "Light Rider Inc Post Quantum Cryptography FIPS 140-3 module with module search capability." A post-quantum-cryptography module (NIST FIPS 140-3 style) with a module-search feature; no accompanying paper found. Related weekly-automation repo gzquse/quantum_news-NIST maintains a NIST PQC standardisation timeline (2015 workshops → FIPS 203/204/205) and translates the PhotonBox Chinese quantum weekly using the Claude API.
- **Thesis theme:** **(E)** PQC / cryptography (software, not a paper).

---

## Part 2. Uncertain / excluded items

| Item | Status | Reason |
|---|---|---|
| Balewski et al., "Quantum-parallel vectorized data encodings and computations on trapped-ion and transmon QPUs", *Sci. Rep.* 14:3435 (2024), DOI 10.1038/s41598-024-53720-x, arXiv:2301.07841 | **Not** a Ziqing Guo paper | Authors are Balewski, Amankwah, Van Beeumen, Bethel, Perciano, Camps. It is, however, the foundational QCrank/QBArt reference cited in Q-GEAR, QPIE, VQT, ShardQ, QAWA. |
| Z. Guo, H. Zhang, X. Zhang, Z. Jin, Q. Wen, "Secure and Efficiently Searchable IoT Communication Data Management Model: Using Blockchain as a new tool", arXiv:1812.08603 (cs.CR, Dec 2018) | **Possibly same person — verify** | Cryptography/blockchain paper with BUPT cryptography faculty (Zhang, Jin, Wen). Consistent with the GitHub account's 2018 creation, early Chinese-language repos and the "quantum cryptography" interest, but no affiliation link to TTU was found. |
| "Ziqing wolfram thoery notebook", Zenodo 10.5281/zenodo.17113876 | Probably his (same ORCID pattern not confirmed) | Wolfram/Mathematica notes; not a publication. |
| Ziqing Guo (KU Leuven): PINN magneto-quasi-static papers (IEEE CEFC 2024; IEEE Trans. Magn. 2025), hysteresis neural operators arXiv:2504.04863, 2604.04150 | **Different person** | Electromagnetics group of Ruth Sabariego. |
| Ziqing Guo et al., J. Cleaner Production 2024 (batch scheduling, wind energy) | **Different person** | Process systems engineering, Dalian. |
| arXiv:2406.08968 (covariate-adaptive randomization), arXiv:2404.13779 (biomedical text mining) | **Different person(s)** | Biostatistics / biomedical NLP. |
| Ziqing Wang & R. Malaney QKD papers (UNSW) | **Different person (different surname)** | Surfaced by fuzzy Crossref search only. |

Not found (searched Crossref, DataCite, arXiv): any journal/conference version of ShardQ, QAWA, NNQA, the nonlinear-waves paper or the QEC audit as of 16 Sept 2026; no standalone QKD paper by Ziqing Guo (QKD appears only through advisor Ziwen Pan's earlier work, e.g. *Phys. Rev. Applied* 14, 024044 (2020), cited in Q-GEAR).

---

## Part 3. GitHub repositories (github.com/gzquse; 143 public repos, account created June 2018)

### Research code (own repositories)
| Repo | Language | Created / last push | What it implements |
|---|---|---|---|
| **qgear** | Python (nbdev), Jupyter | 2024 → active; 241 commits, 7 stars, Apache-2.0 | Q-GEAR: Qiskit→CUDA-Q kernel transformer; gate set H, RY, RZ, U3, CX, CP, SWAP, measure; conda env on `/pscratch`; NERSC Jupyter demos (random circuits, QFT, quantum image encoding). Paper #1. |
| **cudaq-perlmutter** (fork of zohimchandani) | Python | Aug 2024 | Multi-node CUDA-Q execution scripts for Perlmutter (Slurm/MPI). Basis for Q-GEAR containers. |
| **QPIE_datacircuit** | Jupyter/Python | May 2025 | QPIE hybrid network; Dockerfile.pennylane; Shifter PyTorch 24.06 container; Moon/Spiral plotting (`pl_sum.py`); `qpie_model_inference.py`. Paper #2. |
| **DEAL_QUBO** | Python | 2025; 53 commits | DEAL/QAOA for QUBO (TSP, knapsack, MaxCut); `pl_sum.py`, distributed `launch.sh`, D-Wave Leap MVRP annealing benchmark, Qiskit-GPU kernel, IBM hardware job tracking. Paper #3. |
| **quantum-transformer** | Python | Jul 2025 → Aug 2025; 22 commits | VQT: `datacircuits`, `exploratory`, `paper_AAAI2025`, `stable`, `toolbox`; IonQ API submission/retrieval. Paper #4. |
| **paper_AAAI2025-quantum** | Python | 2025 | Figure/data reproduction for VQT (`figB_resIdeal.py`, `figC_resHW.py`, `data_ionq/`). |
| **vectorized_encoding** | Mathematica | Dec 2025 → Jan 2026 | Wolfram notebooks: `quantum_arithmatic_V5.nb` (VQT arithmetic), `qcrank.nb`, `common_decompose.nb` (ShardQ theorems), `algorithms_reference.nb`, `util.wl`. |
| **ShardQ_v2** | Python, MIT | Jan 2026 → Jul 2026 | SparseCut cut selection, hardware-aware (T1/T2, CZ error) optimization, MPS compilation to 100+ qubits, global reconstruction; baselines vs CutQC/random; IBM Heron-r3/r2. Paper #5. |
| **qawa_data_circ** | Python | Oct 2025 → Nov 2025; 1 star | `QAWA_v2.py` minimal Quantum Approximate Walk Algorithm; post-processing/plots; Qiskit 2.2 + Aer HPC backend. Paper #6. |
| **nnqa** | Python, MIT | Mar 2026 | Neural-Native Quantum Arithmetic toolkit: train NN → map weights to circuit angles → quantum weighted-sum/multiply primitives; IBM Heron/Nighthawk cloud jobs. Paper #7. |
| **rubriq-artifact** | Python | Apr 2026 | "SC25 Reproducibility Artifact": GRPO fine-tuning of Qwen2.5-Coder, DeepSeek-Coder-V2-Lite, Llama-3.1-8B, StarCoder2-15B with rubric reward; 21 evaluator tests; 1–2 A100 nodes. Paper #8. |
| **ExploreQEC_mar** | Python, Apache-2.0 | Jun 2026 | "various code for Quantum Error Correction": Stim, Qiskit, Guppy, Squin toolboxes; Steane-code cloud sims (IBM, IQM, Quantinuum); `2026LDRD/docs`, `2026QTML`. Paper #10 context. |
| **qec**, **qec_all** | — | Mar 2026 | Placeholder/empty QEC repos. |
| **quantum_news-NIST** | Python | May 2026 → Sep 2026 | GitHub-Actions jobs: PhotonBox Chinese quantum weekly translator (Claude API) and NIST PQC standardisation timeline/change detector with email digests. Theme E. |
| **llm_cookbook** | Python | Apr 2026 | LLM utilities/notes (supports RubriQ-style work). |
| **qcddl** | HTML | Aug 2025; 9 stars; https://qcddl.ziqguo.com | "Quantum Computing Deadlines Hub" — community deadline tracker for quantum venues (FOCS, STOC, SC, ISCA, MICRO, DAC, ICML, NeurIPS, QCE, journals), CORE ranks, PR-based contributions. |
| **nersc_nbdev**, **NGPU_CUDA_Training**, **sc-dl-playground**, **pytorch_template/wandb**, **hf_template** | Jupyter/CUDA/Python | 2024–2025 | HPC/deep-learning training scaffolding used across projects (NERSC multi-GPU, CUDA training). |
| **gpu-hybrid-computing**, **openmp-series**, **grayScott** (Julia), **IBM-2024-challenge**, **Qworld/qWorld-hack**, **QHACK_stored**, **quantTa**, **qiskit-1.0** | mixed | 2024 | Early quantum/HPC learning and hackathon code. |
| **resume**, **blog**, **gzquse** (profile), **paper-skills**, **music_quiz** | TeX/JS/TS | — | Personal. |

### Notable forks (indicating tool stack)
cuda-quantum (NVIDIA), cuda-q-academic, pennylane-lightning, qiskit-addon-cutting, openqaoa, genQC (generative quantum circuits, Fürrutter), data-encoder-circuits (QCrank/QBArt encoders, Balewski), Stim, tqec, BivariateBicycleCodes, nersc-dl-multigpu, sc24-dl-tutorial, nersc-quantum-day, nanochat/autoresearch (Karpathy), paperdebugger.

---

## Part 4. Key related work seen in these papers (to seed the background bibliography)

### A. HPC / GPU circuit simulation
- J.-S. Kim, A. McCaskey, B. Heim, M. Modani, S. Stanwyck, T. Costa, "CUDA Quantum: The platform for integrated quantum-classical computing," DAC 2023, DOI 10.1109/DAC56929.2023.10247886.
- H. Bayraktar et al., "cuQuantum SDK: A high-performance library for accelerating quantum science," IEEE QCE 2023, pp. 1050–1061, arXiv:2308.01999.
- A. Javadi-Abhari et al., "Quantum computing with Qiskit," arXiv:2405.08810 (2024). (Qiskit Aer GPU used as baseline.)
- A. Asadi et al., "Hybrid quantum programming with PennyLane Lightning on HPC platforms," arXiv:2403.02512 (2024).
- Y. Suzuki et al., "Qulacs: a fast and versatile quantum circuit simulator for research purpose," *Quantum* 5, 559 (2021), arXiv:2011.13524.
- R. Van Beeumen, D. Camps, N. Mehta, "QCLAB++: Simulating quantum circuits on GPUs," arXiv:2303.00123 (2023).
- J. Doi, H. Horii, C. Wood, "Efficient techniques to GPU accelerations of multi-shot quantum computing simulations," arXiv:2308.03399 (2023).
- L. Stephey et al., "Scaling Podman on Perlmutter," CANOPIE-HPC 2022, pp. 41–50.
- M. A. Jette, T. Wickberg, "Architecture of the Slurm workload manager," JSSPP 2023.
- J. Choquette et al., "NVIDIA A100 Tensor Core GPU: Performance and innovation," *IEEE Micro* 41(2), 29–35 (2021).
- M. Mohseni et al., "How to build a quantum supercomputer: Scaling from hundreds to millions of qubits," arXiv:2411.10406 (2024).
- D. Perez-Garcia et al., "Matrix product state representations," quant-ph/0608197.

### B. QAOA / optimization / error mitigation
- E. Farhi, J. Goldstone, S. Gutmann, "A quantum approximate optimization algorithm," arXiv:1411.4028 (2014).
- M. Cerezo et al., "Variational quantum algorithms," *Nat. Rev. Phys.* 3, 625–644 (2021), arXiv:2012.09265.
- J. R. McClean et al., "Barren plateaus in quantum neural network training landscapes," *Nat. Commun.* 9, 4812 (2018), arXiv:1803.11173.
- F. Glover, G. Kochenberger, Y. Du, "A tutorial on formulating and using QUBO models," arXiv:1811.11538.
- J. Weidenfeller et al., "Scaling of the QAOA on superconducting qubit based hardware," *Quantum* 6, 870 (2022), arXiv:2202.03459.
- N. Sachdeva et al., "Quantum optimization using a 127-qubit gate-model IBM quantum computer can outperform quantum annealers …," arXiv:2406.01743.
- J. A. Montañez-Barrera et al., "Unbalanced penalization …," *Quantum Sci. Technol.* 9, 025022 (2024).
- K. Temme, S. Bravyi, J. M. Gambetta, "Error mitigation for short-depth quantum circuits," *PRL* 119, 180509 (2017), arXiv:1612.02058.
- T. Giurgica-Tiron et al., "Digital zero noise extrapolation for quantum error mitigation," IEEE QCE 2020, pp. 306–316, arXiv:2005.10921.
- A. Kandala et al., "Error mitigation extends the computational reach of a noisy quantum processor," *Nature* 567, 491 (2019).
- J. Preskill, "Quantum computing in the NISQ era and beyond," *Quantum* 2, 79 (2018), arXiv:1801.00862.
- A. Abbas et al., "Challenges and opportunities in quantum optimization," *Nat. Rev. Phys.* (2024).
- A. M. Childs, "Universal computation by quantum walk," *PRL* 102, 180501 (2009), arXiv:0806.1972.

### C. Quantum ML / encoding / transformers / circuit cutting
- J. Balewski, M. G. Amankwah, R. Van Beeumen, E. W. Bethel, T. Perciano, D. Camps, "Quantum-parallel vectorized data encodings and computations on trapped-ion and transmon QPUs," *Sci. Rep.* 14, 3435 (2024), DOI 10.1038/s41598-024-53720-x, arXiv:2301.07841. (QCrank/QBArt — central to Q-GEAR, VQT, ShardQ, QAWA, nonlinear-waves.)
- M. G. Amankwah, D. Camps, E. W. Bethel, R. Van Beeumen, T. Perciano, "Quantum pixel representations and compression for N-dimensional images," *Sci. Rep.* 12, 7712 (2022), arXiv:2110.04405.
- J. Balewski, C. Pestano, M. G. Amankwah, E. W. Bethel, T. Perciano, R. Van Beeumen, "EHands: Quantum protocol for polynomial computation on real-valued encoded states," arXiv:2502.15928 (2025).
- J. Balewski et al., "Compilation of QCrank encoding algorithm for a dynamically programmable qubit array processor," arXiv:2507.10699 (2025).
- M. Möttönen, J. J. Vartiainen, V. Bergholm, M. M. Salomaa, "Quantum circuits for general multiqubit gates," *PRL* 93, 130502 (2004) (uniformly controlled rotations).
- D. Camps, R. Van Beeumen, "FABLE: Fast approximate quantum circuits for block encodings," IEEE QCE 2022, pp. 104–113.
- J. Biamonte et al., "Quantum machine learning," *Nature* 549, 195–202 (2017), arXiv:1611.09347.
- M. Schuld, A. Bocharov, K. Svore, N. Wiebe, "Circuit-centric quantum classifiers," *PRA* 101, 032308 (2020).
- A. Mari et al., "Transfer learning in hybrid classical-quantum neural networks," *Quantum* 4, 340 (2020), arXiv:1912.08278.
- G. E. Crooks, "Gradients of parameterized quantum gates using the parameter-shift rule and gate decomposition," arXiv:1905.13311; T. Jones, J. Gacon, "Efficient calculation of gradients in classical simulations of variational quantum algorithms," arXiv:2009.02823.
- A. Vaswani et al., "Attention is all you need," NeurIPS 2017, arXiv:1706.03762.
- N. Khatri, G. Matos, L. Coopmans, S. Clark, "Quixer: A quantum transformer model," arXiv:2406.04305 (2024).
- S. Y.-C. Chen, S. Yoo, Y.-L. L. Fang, "Quantum long short-term memory," ICASSP 2022, arXiv:2009.01783.
- T. Peng, A. W. Harrow, M. Ozols, X. Wu, "Simulating large quantum circuits on a small quantum computer," *PRL* 125, 150504 (2020), arXiv:1904.00102.
- S. Bravyi, G. Smith, J. A. Smolin, "Trading classical and quantum computational resources," *PRX* 6, 021043 (2016).
- K. Mitarai, K. Fujii, "Constructing a virtual two-qubit gate by sampling single-qubit operations," *New J. Phys.* 23, 023021 (2021), arXiv:1909.07534.
- C. Piveteau, D. Sutter, "Circuit knitting with classical communication," *IEEE Trans. Inf. Theory* 70(4), 2734–2745 (2024), arXiv:2205.00016.
- A. Gilyén, Y. Su, G. H. Low, N. Wiebe, "Quantum singular value transformation and beyond," STOC 2019, arXiv:1806.01838.
- A. W. Harrow, A. Hassidim, S. Lloyd, "Quantum algorithm for linear systems of equations," *PRL* 103, 150502 (2009), arXiv:0811.3171.
- F. Fürrutter, G. Muñoz-Gil, H. J. Briegel, "Quantum circuit synthesis with diffusion models," *Nat. Mach. Intell.* 6, 515–524 (2024), arXiv:2311.02041.

### D. QEC
- A. G. Fowler, M. Mariantoni, J. M. Martinis, A. N. Cleland, "Surface codes: Towards practical large-scale quantum computation," *PRA* 86, 032324 (2012), arXiv:1208.0928.
- R. Acharya et al. (Google Quantum AI), "Quantum error correction below the surface code threshold," *Nature* 638, 920–926 (2025), arXiv:2408.13687.
- S. Bravyi, A. W. Cross, J. M. Gambetta, D. Maslov, P. Rall, T. J. Yoder, "High-threshold and low-overhead fault-tolerant quantum memory," *Nature* 627, 778–782 (2024), arXiv:2308.07915 (bivariate bicycle codes).
- C. Gidney, "Stim: a fast stabilizer circuit simulator," *Quantum* 5, 497 (2021), arXiv:2103.02202.
- D. Gottesman, "Stabilizer codes and quantum error correction," PhD thesis, Caltech (1997), quant-ph/9705052.
- A. Y. Kitaev, "Fault-tolerant quantum computation by anyons," *Ann. Phys.* 303, 2–30 (2003), quant-ph/9707021.
- E. Dennis, A. Kitaev, A. Landahl, J. Preskill, "Topological quantum memory," *J. Math. Phys.* 43, 4452 (2002), quant-ph/0110143.
- S. Aaronson, D. Gottesman, "Improved simulation of stabilizer circuits," *PRA* 70, 052328 (2004), quant-ph/0406025.
- B. M. Terhal, "Quantum error correction for quantum memories," *Rev. Mod. Phys.* 87, 307 (2015), arXiv:1302.4011.
- A. R. Calderbank, P. W. Shor, "Good quantum error-correcting codes exist," *PRA* 54, 1098 (1996); A. M. Steane, "Error correcting codes in quantum theory," *PRL* 77, 793 (1996).
- N. Sundaresan et al., "Demonstrating multi-round subsystem quantum error correction using matching and maximum likelihood decoders," *Nat. Commun.* 14, 2852 (2023).

### E. Cryptography / PQC / QKD
- P. W. Shor, "Algorithms for quantum computation: discrete logarithms and factoring," FOCS 1994; *SIAM J. Comput.* 26, 1484 (1997), quant-ph/9508027.
- L. K. Grover, "A fast quantum mechanical algorithm for database search," STOC 1996, quant-ph/9605043.
- C. Gidney, M. Ekerå, "How to factor 2048 bit RSA integers in 8 hours using 20 million noisy qubits," *Quantum* 5, 433 (2021), arXiv:1905.09749.
- NIST FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA), August 2024; NIST FIPS 140-3 (2019); NIST SP 800-90A Rev. 1 (2015).
- U. Vazirani, T. Vidick, "Fully device-independent quantum key distribution," *PRL* 113, 140501 (2014), arXiv:1210.1810.
- U. Mahadev, "Classical verification of quantum computations," FOCS 2018, arXiv:1804.01082.
- A. Broadbent, J. Fitzsimons, E. Kashefi, "Universal blind quantum computation," FOCS 2009, arXiv:0807.4994.
- Z. Pan et al., "Secret-key distillation across a quantum wiretap channel under restricted eavesdropping," *Phys. Rev. Applied* 14, 024044 (2020) (advisor's QKD work).

### F. LLM / RL for code and circuit synthesis; PDE simulation
- Z. Shao et al., "DeepSeekMath: Pushing the limits of mathematical reasoning in open language models," arXiv:2402.03300 (2024) (GRPO).
- DeepSeek-AI, "DeepSeek-R1: Incentivizing reasoning capability in LLMs via reinforcement learning," arXiv:2501.12948 (2025).
- E. J. Hu et al., "LoRA: Low-rank adaptation of large language models," arXiv:2106.09685 (2021).
- S. Rajbhandari et al., "ZeRO: Memory optimizations toward training trillion parameter models," arXiv:1910.02054 (SC 2020).
- G. Strang, "On the construction and comparison of difference schemes," *SIAM J. Numer. Anal.* 5, 506–517 (1968).
- S. Lloyd, "Universal quantum simulators," *Science* 273, 1073–1078 (1996).
- S. Jin, N. Liu, Y. Yu, "Quantum simulation of partial differential equations via Schrödingerization," *PRL* 133, 230602 (2024) (arXiv id TODO).
- M. A. Nielsen, I. L. Chuang, *Quantum Computation and Quantum Information*, Cambridge Univ. Press (2010).

---

## Part 5. Thesis-theme map

| Theme | Papers |
|---|---|
| (A) HPC large-scale circuit simulation | #1 Q-GEAR (primary); #5 ShardQ (GPU knitting); #8 RubriQ (Perlmutter RL + CUDA-Q) |
| (B) QAOA / optimization / NISQ | #3 DEAL (primary); #6 QAWA (primary) |
| (C) QML / transformer / encoding | #2 QPIE; #4 VQT; #5 ShardQ; #7 NNQA |
| (D) QEC | #10 QEC randomness audit |
| (E) Cryptography / PQC / QKD | #10 (threat model, FIPS context); #11 Light Rider QPC SDK; (possibly arXiv:1812.08603) |
| (F) Other | #8 RubriQ (LLM+RL synthesis); #9 nonlinear-wave quantum simulation |

## Part 6. Open items / to verify
1. Canonical ACM DOI for Q-GEAR (main vs. workshop volume) and the workshop name.
2. QST article number/issue for QPIE (volume 10, published 3 Jul 2025).
3. Publication outcome of ShardQ, QAWA, NNQA, nonlinear-waves, QEC-audit preprints; RubriQ status at *npj Quantum Information* and the SC25/SC26 artifact.
4. GitHub repository name for SplitStepQUDE (nonlinear waves) and public repo for the QEC audit.
5. Whether arXiv:1812.08603 (blockchain IoT, BUPT) is the same Ziqing Guo.
6. Citation counts (Semantic Scholar was rate-limited; only QPIE = 4 retrieved).
