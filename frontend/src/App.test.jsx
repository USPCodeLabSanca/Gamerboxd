import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from './App'; // Ajuste o caminho se necessário

describe('Componente App', () => {
    it('deve renderizar corretamente', () => {
        render(<App />);
        // Aqui você pode buscar por um texto que sabe que existe na sua tela inicial
        // Exemplo: expect(screen.getByText(/Gamerboxd/i)).toBeInTheDocument();
        expect(true).toBe(true); // Teste bobo só para garantir que a engrenagem funciona
    });
});