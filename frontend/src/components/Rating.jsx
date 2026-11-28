import { useId } from "react";
import notaIcon from "../assets/icons/nota.svg";

export default function Rating({ value, onChange, disabled = false }) {
    const id = useId();
    const formatted = value.toLocaleString("pt-BR");
    const interactive = !!onChange;
    const size = interactive ? "w-8 h-8" : "w-6 h-6";

    const controls = [1, 2, 3, 4, 5].map((position) => {
        const fill = Math.max(0, Math.min(1, value - position + 1));
        return (
            <span key={position} className={`relative inline-block shrink-0 ${size} ${interactive ? "rounded-sm focus-within:outline-2 focus-within:outline-offset-2 focus-within:outline-roxo" : ""}`}>
                <img src={notaIcon} alt="" aria-hidden="true" className="w-full h-full opacity-20" />
                <img src={notaIcon} alt="" aria-hidden="true" className="absolute inset-0 w-full h-full" style={{ clipPath: `inset(0 ${100 - fill * 100}% 0 0)` }} />
                {interactive && [position - 0.5, position].map((note, half) => (
                    <label key={note} title={`Selecionar ${note.toLocaleString("pt-BR")} de 5`} className={`absolute inset-y-0 w-1/2 ${half === 0 ? "left-0" : "right-0"}`}>
                        <input
                            type="radio"
                            name={id}
                            value={note}
                            checked={value === note}
                            disabled={disabled}
                            onChange={() => onChange(note)}
                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-default"
                        />
                        <span className="sr-only">{note.toLocaleString("pt-BR")} de 5</span>
                    </label>
                ))}
            </span>
        );
    });

    if (!interactive) {
        return <span role="img" aria-label={`Nota: ${formatted} de 5`} className="inline-flex items-center gap-1">{controls}</span>;
    }

    return (
        <div role="radiogroup" aria-label="Nota" className="flex flex-col items-start gap-2">
            <span aria-live="polite" className="text-sm text-white/80">Nota: {formatted} de 5</span>
            <div className="flex items-center gap-1">{controls}</div>
            <div className="flex items-center gap-3 text-xs text-white/60">
                <label className="relative text-roxo underline rounded-sm focus-within:outline-2 focus-within:outline-offset-2 focus-within:outline-roxo">
                    <input type="radio" name={id} value={0} checked={value === 0} disabled={disabled} onChange={() => onChange(0)} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-default" />
                    <span aria-hidden="true">Limpar nota</span><span className="sr-only">0 de 5</span>
                </label>
            </div>
        </div>
    );
}
