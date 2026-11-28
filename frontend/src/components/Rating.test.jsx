// @vitest-environment node
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import Rating from './Rating';

describe('controles de avaliação', () => {
    it.each([
        [0, [100, 100, 100, 100, 100]],
        [2.5, [0, 0, 50, 100, 100]],
        [3.5, [0, 0, 0, 50, 100]],
        [5, [0, 0, 0, 0, 0]],
    ])('representa a nota %s com cinco controles e recorte correto da metade', (value, expected) => {
        const html = renderToStaticMarkup(<Rating value={value} />);
        const clips = [...html.matchAll(/clip-path:inset\(0 (\d+)% 0 0\)/g)].map((match) => Number(match[1]));
        expect(clips).toEqual(expected);
        expect(html).toContain(`aria-label="Nota: ${value.toLocaleString('pt-BR')} de 5"`);
        expect(html).not.toContain('type="radio"');
    });

    it.each([2.5, 3.5, 5])('preenche a nota salva %s e oferece apenas opções de meia nota', (value) => {
        const html = renderToStaticMarkup(<Rating value={value} onChange={() => {}} />);
        expect(html).toContain('role="radiogroup"');
        expect(html).not.toContain('Cada metade vale');
        expect(html).not.toContain('aria-describedby');
        expect([...html.matchAll(/value="([\d.]+)"/g)].map((match) => Number(match[1]))).toEqual([0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 0]);
        expect(html).toMatch(new RegExp(`checked="" value="${value}"`));
        expect(html.match(/checked=""/g)).toHaveLength(1);
    });

    it('desabilita todas as opções enquanto o formulário salva', () => {
        const html = renderToStaticMarkup(<Rating value={2.5} onChange={() => {}} disabled />);
        expect(html.match(/disabled=""/g)).toHaveLength(11);
    });
});
