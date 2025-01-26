import { Atom, Brain, Zap } from "lucide-react";

export interface Paper {
    id: number;
    title: string;
    summary: string;
    url: string;
    publishedDate: string;
    domain: string;
}

export type LucideIcon = React.ComponentType<{
    className?: string;
    size?: number;
}>;

export const domainIcons: Record<string, LucideIcon> = {
    "Machine Learning": Atom,
    "Quantum Computing": Brain,
    "AI Sustainability": Zap,
};