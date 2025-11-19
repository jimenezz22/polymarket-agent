# 🧪 Testing Guide - Polymarket AI Hedge Agent

**GUÍA SIMPLIFICADA PARA EJECUTAR TESTS**

---

## ✅ Pre-requisitos

Ya completaste:
- ✅ Setup ejecutado (`./setup.sh`)
- ✅ Dependencias instaladas
- ✅ `.env` configurado con mercado real
- ✅ Virtual environment activo

---

## 🚀 FORMA RÁPIDA - TODO EN 1 COMANDO

### **Opción 1: Ejecutar TODOS los tests** ⭐ **RECOMENDADO**

```bash
./run_tests.sh
```

**Qué hace:**
- ✅ Quick tests (6 tests en 5 segundos)
- ✅ Strategy tests (3 scenarios)
- ✅ Position tests (5 tests)

**Total:** 14 tests en ~10 segundos

**Resultado esperado:**
```
🧪 Running Polymarket Agent Tests
==================================

📋 Running quick tests...
✅ ALL QUICK TESTS PASSED!

📋 Running strategy tests...
✅ All Phase 3 strategy tests passed!

📋 Running position tests...
✅ All Phase 2 tests passed!

==================================
✅ ALL TESTS PASSED!
==================================
```

---

### **Opción 2: Quick Test (Solo lo esencial)**

```bash
python3 test_quick.py
```

**Qué prueba (6 tests):**
1. ✅ Imports
2. ✅ Configuration
3. ✅ Gamma API
4. ✅ Hedge math (1250→7679)
5. ✅ Position management
6. ✅ Strategy logic

**Tiempo:** 5 segundos

---

## 📋 TESTS INDIVIDUALES (Si quieres ejecutar por separado)

### **Opción A: Con el script wrapper**

```bash
# Solo strategy tests
PYTHONPATH=. python3 tests/test_strategy.py

# Solo position tests
PYTHONPATH=. python3 tests/test_position.py
```

### **Opción B: Usar run_tests.sh** (más fácil)

```bash
# Ejecuta todos
./run_tests.sh
```

---

## 🎯 PASO A PASO DETALLADO

### **PASO 1: Quick Test** ⏱️ 5 segundos

```bash
python3 test_quick.py
```

**Deberías ver:**
```
============================================================
🧪 QUICK TESTS - Polymarket Hedge Agent
============================================================

1️⃣ Testing imports...
   ✅ All imports successful

2️⃣ Testing configuration...
   ✓ Market ID: 0x39d45b454dcf932767...
   ✓ Chain: 80002 (Polygon Amoy Testnet)
   ✓ Take Profit: 85.0%
   ✓ Stop Loss: 78.0%
   ✅ Config loaded correctly

3️⃣ Testing Gamma API...
   ✓ Market: [Nombre del mercado]
   ✓ YES: [precio] %
   ✓ NO: [precio] %
   ✅ Gamma API works!

4️⃣ Testing hedge calculations...
   ✓ Input: 1250 YES @ $0.86
   ✓ Output: Sell 1250 YES → Buy 7679 NO
   ✓ Proceeds: $1,075.00
   ✅ Math is correct!

5️⃣ Testing position management...
   ✓ Created position: 1250 YES
   ✓ Total invested: $1,000.00
   ✓ Unrealized PnL: $75.00
   ✅ Position management works!

6️⃣ Testing strategy logic...
   ✓ Should take profit at 86%: True
   ✓ Should stop loss at 76%: True
   ✓ Action at 86%: TAKE_PROFIT
   ✅ Strategy logic works!

============================================================
✅ ALL QUICK TESTS PASSED!
============================================================
```

---

### **PASO 2: Full Test Suite** ⏱️ 10 segundos

```bash
./run_tests.sh
```

**Deberías ver:**

#### A. Quick Tests (ya vistos arriba)

#### B. Strategy Tests - 3 Scenarios

**Scenario 1: Take Profit (80% → 86%)**
```
╭─────────────────────────────────────────────╮
│ Scenario 1: Take Profit & Hedge (80% → 86%) │
╰─────────────────────────────────────────────╯

📊 Step 1: Entry
  BUY 1250 YES @ $0.80 = $1,000

📊 Step 2: Price → 82% (HOLD)
  Action: HOLD
  Unrealized PnL: +$25.00

📊 Step 3: Price → 86% (TAKE PROFIT)
  ✓ Take-profit triggered!
  Sell 1250 YES @ $0.86 → $1,075
  Buy 7679 NO @ $0.14
  Locked PnL: [calculated]

📈 Final Outcome Scenarios:
  If YES wins: $[amount]
  If NO wins: +$6,603.57
```

**Scenario 2: Stop Loss (80% → 76%)**
```
╭───────────────────────────────────╮
│ Scenario 2: Stop Loss (80% → 76%) │
╰───────────────────────────────────╯

📊 Step 1: Entry
  BUY 1250 YES @ $0.80

📊 Step 2: Price → 76% (STOP LOSS)
  ⚠ Stop-loss triggered!
  Sell 1250 YES @ $0.76 → $950
  Final PnL: -$50.00
  💡 Loss minimized by exiting early
```

**Scenario 3: Hedge Protection (85% → 50%)**
```
╭──────────────────────────────────────────────────╮
│ Scenario 3: Hedge Protection (85% → Hedge → 50%) │
╰──────────────────────────────────────────────────╯

📊 Step 1: Entry @ 80%
  BUY 1250 YES @ $0.80

📊 Step 2: Price → 85% (HEDGE)
  Sell 750 YES (60%) @ $0.85
  Buy 4250 NO @ $0.15
  Locked PnL: +$25.00

📊 Step 3: Price crashes → 50%
  Net PnL: +$1,375.00
  ✓ Protected by hedge!

📈 Final Outcomes:
  If YES wins: -$500.00
  If NO wins: +$3,250.00
```

#### C. Position Tests

```
✓ PASS - Position Creation
✓ PASS - PnL Calculations
✓ PASS - Hedging Simulation
✓ PASS - Stop Loss Simulation
✓ PASS - Position Persistence

✅ All Phase 2 tests passed!
```

---

### **PASO 3: Test Main Loop (Demo Mode)** ⏱️ Manual

```bash
python main.py
```

**Qué hace:**
- Conecta al mercado real (Buffalo Bills)
- Fetches precios cada 20 segundos
- Muestra status con tablas Rich
- **NO ejecuta trades** (Demo Mode)

**Para detener:** `Ctrl+C`

**Deberías ver:**
```
╔══════════════════════════════════════════════════════════╗
║           POLYMARKET AI HEDGE AGENT - Poll #1            ║
╚══════════════════════════════════════════════════════════╝

ℹ Timestamp: 14:23:45 UTC
ℹ Uptime: 5s

📊 Market Data
Current Probability    9.5%
YES Price             $0.0950
NO Price              $0.9050

🎯 Recommended Action
Action    WAIT
Reason    No position to manage

⚠ DEMO MODE: Trade execution disabled
Next poll in 20s...

[Ctrl+C para detener]
```

---

## 📊 RESUMEN DE COMANDOS

### **Ejecutar TODO (Recomendado)** ⭐

```bash
./run_tests.sh
```

### **Solo Quick Test**

```bash
python3 test_quick.py
```

### **Solo Strategy Tests**

```bash
PYTHONPATH=. python3 tests/test_strategy.py
```

### **Solo Position Tests**

```bash
PYTHONPATH=. python3 tests/test_position.py
```

### **Main Loop (Demo)**

```bash
python main.py
```

---

## ✅ Checklist de Testing

Marca cuando completes:

- [ ] ✅ `python3 test_quick.py` - Todos los tests pasan
- [ ] ✅ `./run_tests.sh` - Suite completa pasa
- [ ] ✅ `python main.py` - Demo mode funciona
- [ ] ✅ Ctrl+C hace shutdown limpio
- [ ] ✅ Resultados documentados

---

## 🚨 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'my_agent'"

**Solución:** Usa `./run_tests.sh` en vez de ejecutar directamente

O:
```bash
PYTHONPATH=. python3 tests/test_strategy.py
```

### Error: "Command not found: python"

**Solución:** Usa `python3` en vez de `python`

```bash
python3 test_quick.py
```

### Tests fallan

**Solución:**
1. Verifica que venv esté activo: `source venv/bin/activate`
2. Reinstala deps: `pip install -r requirements.txt`
3. Ejecuta quick test primero: `python3 test_quick.py`

---

## 📝 Siguiente Paso

Después de que todos los tests pasen:

1. **Documentar resultados:**
   ```bash
   # Los resultados ya están en tests/report.md
   cat tests/report.md
   ```

2. **Crear DISCUSSION.md:**
   ```bash
   nano docs/DISCUSSION.md
   # Documenta riesgos y mejoras
   ```

3. **Push a GitHub:**
   ```bash
   git add .
   git commit -m "test: all tests passing"
   git push
   ```

---

## 🎯 COMANDOS ESENCIALES (Copia estos)

```bash
# 1. Quick test (5 seg)
python3 test_quick.py

# 2. Full suite (10 seg)
./run_tests.sh

# 3. Demo mode (manual, Ctrl+C para parar)
python main.py

# ✅ DONE!
```

---

**¿Todos los tests pasaron? ✅ Estás listo para deployment!** 🚀
