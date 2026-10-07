import {
  STRIPS, PAYLINES, PAYTABLE, SCATTER_PAYS, WILD, SCATTER,
  evaluateLine, evaluateGrid, gridFromStops, spinReels, theoreticalRtp,
} from './slotMath';

// Seeded LCG so the simulation check is reproducible.
const lcg = (seed) => () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 2 ** 32);

describe('Piedra del Sol math contract', () => {
  test('strips are complete and each carries exactly one scatter', () => {
    expect(STRIPS).toHaveLength(5);
    STRIPS.forEach((strip) => {
      expect(strip.every(Boolean)).toBe(true);
      expect(strip.filter((s) => s === SCATTER)).toHaveLength(1);
    });
  });

  test('line evaluation: plain, wild-substituted, pure wild, and broken runs', () => {
    expect(evaluateLine(['jaguar', 'jaguar', 'jaguar', 'nopal', 'nopal']).pay).toBe(PAYTABLE.jaguar[0]);
    expect(evaluateLine([WILD, 'rosa', WILD, 'rosa', 'rosa']).pay).toBe(PAYTABLE.rosa[2]);
    expect(evaluateLine([WILD, WILD, WILD, WILD, 'nopal']).pay).toBe(PAYTABLE.sol[1]);
    expect(evaluateLine(['chile', 'maiz', 'chile', 'chile', 'chile']).pay).toBe(0);
    expect(evaluateLine([SCATTER, SCATTER, SCATTER, 'maiz', 'maiz']).pay).toBe(0);
  });

  test('a wild run takes the better of the wild pay and the substituted pay', () => {
    // 3 wilds + 2 jaguars: 5x jaguar (750) beats 3x wild (50).
    expect(evaluateLine([WILD, WILD, WILD, 'jaguar', 'jaguar'])).toMatchObject({ symbol: 'jaguar', count: 5 });
    // 4 wilds + nopal: 4x wild (200) beats 5x nopal (25).
    expect(evaluateLine([WILD, WILD, WILD, WILD, 'nopal'])).toMatchObject({ symbol: WILD, count: 4 });
  });

  test('grid evaluation pays lines at totalBet/10 and scatters at totalBet', () => {
    const grid = Array.from({ length: 5 }, () => ['nopal', 'jaguar', 'chile']);
    grid[0][0] = SCATTER; grid[2][2] = SCATTER; grid[4][0] = SCATTER;
    const result = evaluateGrid(grid, 10);
    expect(result.scatters).toBe(3);
    expect(result.scatterPay).toBe(SCATTER_PAYS[3] * 10);
    const midLine = result.wins.find((w) => w.line === 0);
    expect(midLine).toMatchObject({ symbol: 'jaguar', count: 5, amount: PAYTABLE.jaguar[2] });
  });

  test('every payline reads a valid row on every reel', () => {
    PAYLINES.forEach((line) => {
      expect(line).toHaveLength(5);
      line.forEach((row) => expect([0, 1, 2]).toContain(row));
    });
    expect(gridFromStops([0, 0, 0, 0, 0]).every((col) => col.length === 3)).toBe(true);
  });

  test('theoretical RTP sits in the 95-98% design band', () => {
    const { total } = theoreticalRtp();
    expect(total).toBeGreaterThan(0.95);
    expect(total).toBeLessThan(0.98);
  });

  test('simulation agrees with the exact RTP', () => {
    const rng = lcg(113);
    let bet = 0;
    let won = 0;
    for (let i = 0; i < 100000; i++) {
      bet += 10;
      won += evaluateGrid(spinReels(rng).grid, 10).total;
    }
    expect(Math.abs(won / bet - theoreticalRtp().total)).toBeLessThan(0.03);
  });
});
