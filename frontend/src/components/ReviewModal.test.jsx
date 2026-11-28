import { fireEvent, render, screen, cleanup } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { afterEach, describe, expect, it } from 'vitest';
import ReviewModal from './ReviewModal';

afterEach(cleanup);

function renderModal(props = {}) {
    return render(
        <QueryClientProvider client={new QueryClient()}>
            <ReviewModal game={{ id: 1, title: 'Jogo de teste' }} isOpen onClose={() => {}} {...props} />
        </QueryClientProvider>
    );
}

describe('formulário de review', () => {
    it('carrega todos os campos editáveis, incluindo valores nulos e nota fracionada', () => {
        renderModal({ review: { review_id: 'review', rating_num: 3.5, rating_text: null, liked: true, completed: true, privacy: 40, time_played: null } });
        expect(screen.getByRole('radio', { name: '3,5 de 5', exact: true })).toBeChecked();
        expect(screen.getByLabelText('Review')).toHaveValue('');
        expect(screen.getByLabelText('Tempo jogado (horas)')).toHaveValue(null);
        expect(screen.getByLabelText('Privacidade')).toHaveValue('40');
        expect(screen.getByLabelText('Curti o jogo')).toBeChecked();
        expect(screen.getByLabelText('Completei o jogo')).toBeChecked();
    });
    it('seleciona meias notas e mantém as restrições de texto e horas', () => {
        renderModal();
        expect(screen.getByRole('radio', { name: '0 de 5', exact: true })).toBeChecked();
        for (const value of ['2,5', '3,5', '5', '0']) {
            const option = screen.getByRole('radio', { name: `${value} de 5`, exact: true });
            fireEvent.click(option);
            expect(option).toBeChecked();
            expect(screen.getByText(`Nota: ${value} de 5`)).toBeInTheDocument();
        }
        expect(screen.queryByLabelText('Rating (0 a 5)')).not.toBeInTheDocument();
        expect(screen.getByLabelText('Review')).toHaveAttribute('maxLength', '300');
        const hours = screen.getByLabelText('Tempo jogado (horas)');
        fireEvent.change(hours, { target: { value: '-1' } });
        expect(hours.checkValidity()).toBe(false);
    });
    it('preenche a marcação solicitada pelo botão Completei ao editar', () => {
        renderModal({ completed: true, review: { review_id: 'review', rating_num: 3, completed: false } });
        expect(screen.getByLabelText('Completei o jogo')).toBeChecked();
    });
    it('preserva o texto ao alterar progresso, curtida, horas, privacidade e meia nota', () => {
        renderModal();
        const text = screen.getByLabelText('Review');
        fireEvent.change(text, { target: { value: 'Meu texto continua aqui.' } });
        fireEvent.click(screen.getByRole('checkbox', { name: 'Completei o jogo' }));
        fireEvent.click(screen.getByRole('checkbox', { name: 'Curti o jogo' }));
        fireEvent.change(screen.getByLabelText('Tempo jogado (horas)'), { target: { value: '12' } });
        fireEvent.change(screen.getByLabelText('Privacidade'), { target: { value: '40' } });
        fireEvent.click(screen.getByRole('radio', { name: '2,5 de 5', exact: true }));
        expect(text).toHaveValue('Meu texto continua aqui.');
        expect(screen.getByRole('checkbox', { name: 'Completei o jogo' })).toBeChecked();
        expect(screen.getByRole('checkbox', { name: 'Curti o jogo' })).toBeChecked();
        expect(screen.queryByRole('checkbox', { name: 'Jogou' })).not.toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'Jogou' })).not.toBeInTheDocument();
        expect(screen.queryByText('100%')).not.toBeInTheDocument();
    });
    it('mantém a navegação por Tab dentro do modal', () => {
        renderModal();
        const save = screen.getByRole('button', { name: 'Salvar review' });
        const close = screen.getByRole('button', { name: 'Fechar' });
        save.focus();
        fireEvent.keyDown(save, { key: 'Tab' });
        expect(close).toHaveFocus();
        fireEvent.keyDown(close, { key: 'Tab', shiftKey: true });
        expect(save).toHaveFocus();
    });
    it('descarta o rascunho ao fechar e reabrir, sem enviar campos sem suporte', () => {
        const view = renderModal();
        fireEvent.change(screen.getByLabelText('Review'), { target: { value: 'Rascunho' } });
        view.unmount();
        renderModal();
        expect(screen.getByLabelText('Review')).toHaveValue('');
        expect(screen.queryByText('Jogado em:')).not.toBeInTheDocument();
    });
});
