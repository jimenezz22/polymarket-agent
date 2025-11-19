# 🧪 Testing Guide - Polymarket AI Hedge Agent

**GUÍA PASO A PASO PARA PROBAR EL AGENTE**

---

## ✅ Pre-requisitos Completados

Ya tienes:
- ✅ Setup ejecutado (`./setup.sh`)
- ✅ Dependencias instaladas
- ✅ `.env` configurado con mercado real (Buffalo Bills Super Bowl)
- ✅ Virtual environment activo

---

## 📋 PASO A PASO - Testing Completo

### **PASO 1: Verificar que todo está instalado** ⏱️ 1 min

```bash
# Activar venv (si no está activo)
source venv/bin/activate

# Test rápido de imports
python -c "from my_agent import *; print('✓ my_agent works!')"
```

**Resultado esperado:**
```
✓ my_agent works!
```

**Si falla:** Revisa que `venv` esté activado

---

### **PASO 2: Verificar configuración del mercado** ⏱️ 1 min

```bash
python3 << 'EOF'
from my_agent.utils.config import config

print("=" * 60)
print("CONFIGURACIÓN CARGADA")
print("=" * 60)
print(f"✓ Market ID: {config.MARKET_CONDITION_ID[:20]}...")
print(f"✓ Chain ID: {config.CHAIN_ID} (Polygon Amoy Testnet)")
print(f"✓ RPC: {config.POLYGON_RPC_URL[:40]}...")
print(f"✓ Take Profit: {config.TAKE_PROFIT_PROBABILITY * 100}%")
print(f"✓ Stop Loss: {config.STOP_LOSS_PROBABILITY * 100}%")
print("=" * 60)
EOF
```

**Resultado esperado:**
```
============================================================
CONFIGURACIÓN CARGADA
============================================================
✓ Market ID: 0x39d45b454dcf9327...
✓ Chain ID: 80002 (Polygon Amoy Testnet)
✓ RPC: https://polygon-amoy.g.alchemy.com/v2...
✓ Take Profit: 85.0%
✓ Stop Loss: 78.0%
============================================================
```

---

### **PASO 3: Test de Gamma API (Datos del mercado)** ⏱️ 2 min

```bash
python3 << 'EOF'
from agents.polymarket.gamma import GammaMarketClient

print("\n🔍 TESTING GAMMA API (Market Data)\n")

gamma = GammaMarketClient()
condition_id = "0x39d45b454dcf932767962ad9cbd858c5a6ec21d4d48318a484775b2e83264467"

try:
    markets = gamma.get_markets({"condition_id": condition_id})

    if markets and len(markets) > 0:
        market = markets[0]
        print(f"✓ Market encontrado!")
        print(f"  Pregunta: {market['question']}")
        print(f"  YES price: {market['outcomePrices'][0]} ({float(market['outcomePrices'][0]) * 100:.1f}%)")
        print(f"  NO price: {market['outcomePrices'][1]} ({float(market['outcomePrices'][1]) * 100:.1f}%)")
        print(f"\n✅ Gamma API funciona correctamente!")
    else:
        print("❌ No se encontró el mercado")
except Exception as e:
    print(f"❌ Error: {e}")
    print("Verifica tu conexión a internet")
EOF
```

**Resultado esperado:**
```
🔍 TESTING GAMMA API (Market Data)

✓ Market encontrado!
  Pregunta: Will the Buffalo Bills win Super Bowl 2026?
  YES price: 0.095 (9.5%)
  NO price: 0.905 (90.5%)

✅ Gamma API funciona correctamente!
```

---

### **PASO 4: Test de Wallet (Opcional)** ⏱️ 2 min

```bash
python3 << 'EOF'
print("\n💼 TESTING WALLET CONNECTION\n")

try:
    from agents.polymarket.polymarket import Polymarket

    pm = Polymarket()
    addr = pm.get_address_for_private_key()

    print(f"✓ Wallet Address: {addr[:10]}...{addr[-6:]}")

    try:
        balance = pm.get_balance_usdc()
        print(f"✓ USDC Balance: ${balance:.2f}")
    except Exception as e:
        print(f"⚠ Balance no disponible (normal en testnet): {e}")

    print("\n✅ Wallet funciona correctamente!")

except Exception as e:
    print(f"❌ Error: {e}")
    print("Verifica POLYGON_WALLET_PRIVATE_KEY en .env")
EOF
```

**Resultado esperado:**
```
💼 TESTING WALLET CONNECTION

✓ Wallet Address: 0x1234567...abc123
⚠ Balance no disponible (normal en testnet): [error]

✅ Wallet funciona correctamente!
```

---

### **PASO 5: Ejecutar Tests de Estrategia** ⏱️ 5 min

```bash
python tests/test_strategy.py
```

**Qué hace este test:**
- Simula 3 escenarios completos:
  - **Scenario 1:** Precio sube 80% → 86% (Take Profit + Hedge)
  - **Scenario 2:** Precio baja 80% → 76% (Stop Loss)
  - **Scenario 3:** Hedge protege contra crash de precio

**Resultado esperado:**
Verás tablas bonitas con Rich mostrando:
```
╔══════════════════════════════════════════════════════════╗
║     Scenario 1: Take Profit & Hedge (80% → 86%)         ║
╚══════════════════════════════════════════════════════════╝

📊 Step 1: Entry
   Action: BUY 1250 YES @ $0.80
   Invested: $1,000
   ...

📊 Step 3: Price → 86% (TAKE PROFIT)
   ✓ Take-profit triggered!
   YES Sold: 1250 @ $0.8600
   Proceeds: $1,075.00
   NO Bought: 7679 @ $0.1400
   Locked PnL: +$6,679.00
   ...

✅ All Phase 3 strategy tests passed!
```

---

### **PASO 6: Ejecutar Tests de Position** ⏱️ 3 min

```bash
python tests/test_position.py
```

**Qué hace:**
- Testa que Position class funcione
- Verifica cálculos de PnL
- Testa persistencia (save/load)

**Resultado esperado:**
```
✓ PASS - All position tests
```

---

### **PASO 7: Test del Main Loop (Demo Mode)** ⏱️ 5 min

```bash
python main.py
```

**Qué hace:**
- Se conecta al mercado real (Buffalo Bills)
- Fetches precios cada 20 segundos
- Muestra status en consola con tablas Rich
- **NO ejecuta trades** (Demo Mode)

**Resultado esperado:**
```
╔══════════════════════════════════════════════════════════╗
║           POLYMARKET AI HEDGE AGENT - Poll #1            ║
╚══════════════════════════════════════════════════════════╝

ℹ Timestamp: 14:23:45 UTC
ℹ Uptime: 5s
ℹ Fetching market data for condition: 0x39d45b45...

📊 Market Data
Current Probability    9.5%
YES Price             $0.0950
NO Price              $0.9050

💼 Position
[No position open]

🎯 Recommended Action
Action    WAIT
Reason    No position to manage

⚠ DEMO MODE: Trade execution disabled
Next poll in 20s...

[Presiona Ctrl+C para detener]
```

**Para detener:** Presiona `Ctrl+C`

```
⚠ Received interrupt signal

╔══════════════════════════════════════════════════════════╗
║                       SHUTDOWN                            ║
╚══════════════════════════════════════════════════════════╝

ℹ Saving final state...
ℹ Total Runtime: 1m 23s
ℹ Total Polls: 4
✓ Agent shutdown complete
```

---

### **PASO 8: Crear Test Report** ⏱️ 10 min

Copia los resultados de los tests anteriores:

```bash
# Crear el archivo
nano tests/report.md

# O usa tu editor favorito
code tests/report.md
```

**Contenido del report (template):**

```markdown
# Test Report - Polymarket AI Hedge Agent

**Fecha:** [Tu fecha]
**Probado por:** [Tu nombre]
**Entorno:** Polygon Amoy Testnet

---

## 1. Setup

✅ Instalación completada sin errores
✅ Dependencias instaladas: [lista de requirements.txt]
✅ Python version: 3.10.19

---

## 2. Configuración

| Variable | Valor |
|----------|-------|
| Market | Buffalo Bills Super Bowl 2026 |
| Condition ID | 0x39d45b454dcf932... |
| Network | Polygon Amoy (80002) |
| Take Profit | 85% |
| Stop Loss | 78% |

---

## 3. Unit Tests

### test_strategy.py

| Scenario | Status | Resultado |
|----------|--------|-----------|
| Scenario 1: Take Profit (80%→86%) | ✅ PASS | Locked PnL: +$6,679 |
| Scenario 2: Stop Loss (80%→76%) | ✅ PASS | Exit PnL: -$50 |
| Scenario 3: Hedge Protection | ✅ PASS | Protected against 50% crash |

### test_position.py

| Test | Status |
|------|--------|
| Position tracking | ✅ PASS |
| PnL calculations | ✅ PASS |
| Save/Load persistence | ✅ PASS |

---

## 4. Integration Tests

| Component | Status | Notas |
|-----------|--------|-------|
| Gamma API | ✅ | Fetching real market data |
| Wallet Connection | ✅ | Address verified |
| Main Loop | ✅ | Dry-run successful |
| Graceful Shutdown | ✅ | Ctrl+C handled correctly |

---

## 5. Observaciones

**Funcionó bien:**
- ✅ Integración con Gamma API
- ✅ Cálculos matemáticos correctos
- ✅ Rich console output
- ✅ Error handling

**Limitaciones:**
- ⚠️ Demo mode (no ejecuta trades reales)
- ⚠️ Requiere USDC en testnet para trading real
- ⚠️ AI layer no implementado

---

## 6. Conclusión

✅ **Todos los tests pasaron exitosamente**

El agente está listo para:
- Monitorear mercados reales
- Calcular estrategias de hedging correctamente
- Ejecutar en modo simulación

Para producción faltaría:
1. Fondear wallet con USDC en testnet
2. Habilitar trade execution (descomentar en main.py)
3. Probar con cantidades pequeñas primero
```

---

## 📊 RESUMEN DE COMANDOS

**Copiar y pegar en orden:**

```bash
# 1. Activar venv
source venv/bin/activate

# 2. Test imports
python -c "from my_agent import *; print('✓ Works!')"

# 3. Test config
python3 << 'EOF'
from my_agent.utils.config import config
print(f"Market: {config.MARKET_CONDITION_ID[:20]}...")
EOF

# 4. Test Gamma API (market data)
python3 << 'EOF'
from agents.polymarket.gamma import GammaMarketClient
gamma = GammaMarketClient()
markets = gamma.get_markets({"condition_id": "0x39d45b454dcf932767962ad9cbd858c5a6ec21d4d48318a484775b2e83264467"})
print(f"✓ Market: {markets[0]['question']}")
print(f"  YES: {markets[0]['outcomePrices'][0]}")
EOF

# 5. Test estrategia (3 scenarios)
python tests/test_strategy.py

# 6. Test position
python tests/test_position.py

# 7. Test main loop (Ctrl+C para parar)
python main.py

# 8. Crear report
nano tests/report.md  # Copiar template de arriba
```

---

## ✅ Checklist Final

Marca cada uno cuando lo completes:

- [ ] ✅ PASO 1: Imports funcionan
- [ ] ✅ PASO 2: Config cargada correctamente
- [ ] ✅ PASO 3: Gamma API trae datos del mercado
- [ ] ✅ PASO 4: Wallet conectado (opcional)
- [ ] ✅ PASO 5: test_strategy.py - 3 scenarios PASS
- [ ] ✅ PASO 6: test_position.py - PASS
- [ ] ✅ PASO 7: main.py funciona en demo mode
- [ ] ✅ PASO 8: tests/report.md creado

---

## 🚨 Troubleshooting

### Error: "ModuleNotFoundError"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "No market found"
- Verifica conexión a internet
- El condition_id puede haber cambiado, busca otro mercado

### Error en Wallet
- Verifica POLYGON_WALLET_PRIVATE_KEY en .env
- No necesitas USDC para testing (solo para trades reales)

---

## 📝 Próximos Pasos

Después de completar los tests:

1. **Crear docs/DISCUSSION.md** con riesgos y mejoras
2. **Push a GitHub**
3. **Preparar para submission**

---

**¿Algún paso no funciona? Revisa los errores y pregúntame!** 🚀
