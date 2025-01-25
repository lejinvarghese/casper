import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardHeader, CardTitle, CardContent } from "./components/ui/Card";
import {
    BookOpen,
    CalendarDays,
    Link2,
    Atom,
    Brain,
    Zap,
    RefreshCw,
} from "lucide-react";

// Background Component
const AnimatedBackground: React.FC = () => {
    return (
        <svg
            className="fixed inset-0 z-0 w-full h-full"
            style={{ pointerEvents: "none" }}
        >
            <defs>
                <filter id="blurFilter">
                    <feGaussianBlur in="SourceGraphic" stdDeviation="1" />
                </filter>
            </defs>
            {[...Array(50)].map((_, index) => {
                const x = Math.random() * 100;
                const y = Math.random() * 100;
                const size = Math.random() * 10 + 2;
                const opacity = Math.random() * 0.5 + 0.1;
                const animationDelay = Math.random() * 5;

                return (
                    <motion.circle
                        key={index}
                        cx={`${x}%`}
                        cy={`${y}%`}
                        r={size / 2}
                        fill="#4287f5"
                        opacity={opacity}
                        initial={{ scale: 0 }}
                        animate={{
                            scale: [0, 1.5, 1],
                            x: [`${x}%`, `${x + (Math.random() * 10 - 5)}%`],
                            y: [`${y}%`, `${y + (Math.random() * 10 - 5)}%`],
                        }}
                        transition={{
                            duration: 5,
                            repeat: Infinity,
                            repeatType: "reverse",
                            delay: animationDelay,
                        }}
                        style={{ filter: "url(#blurFilter)" }}
                    />
                );
            })}
        </svg>
    );
};

const INITIAL_MOCK_PAPERS = [
    {
        id: 1,
        title: "Titans: Learning to Memorize at Test Time",
        summary:
            "The authors introduce Titans, a new neural architecture combining short-term attention and long-term neural memory to improve context modeling. Their neural memory module enables fast parallel training and inference. Experimental results show Titans outperform Transformers and linear recurrent models across multiple tasks, scaling effectively to larger context windows.",
        url: "https://arxiv.org/abs/2501.00663",
        publishedDate: "2024-01-15",
        domain: "Machine Learning",
    },
    {
        id: 2,
        title: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning",
        summary:
            "The authors introduce DeepSeek-R1, a reasoning model trained via reinforcement learning (RL). DeepSeek-R1-Zero, trained without supervised fine-tuning, shows strong reasoning but faces readability and language mixing issues. DeepSeek-R1, with multi-stage training, improves these issues and matches OpenAI-o1-1217 on reasoning tasks. Both models and six distilled versions are open-sourced.",
        url: "https://arxiv.org/abs/2501.12948",
        publishedDate: "2024-01-22",
        domain: "Quantum Computing",
    },
    {
        id: 3,
        title: "Towards Federated Multi-Armed Bandit Learning for Content Dissemination using Swarm of UAVs",
        summary:
            "The paper presents a UAV-based content management system for disaster scenarios, combining stationary anchor UAVs and mobile micro-UAVs to ensure content access in isolated communities. It uses Federated Multi-Armed Bandit learning to optimize content caching based on user demand and content popularity. A Selective Caching Algorithm reduces redundancy, enhancing adaptability to diverse user preferences. The architecture's performance is verified across various network sizes and content patterns.",
        url: "https://arxiv.org/abs/2501.09146",
        publishedDate: "2024-01-18",
        domain: "AI Sustainability",
    },
];

type LucideIcon = React.ComponentType<{
    className?: string;
    size?: number;
}>;

const domainIcons: Record<string, LucideIcon> = {
    "Machine Learning": Atom,
    "Quantum Computing": Brain,
    "AI Sustainability": Zap,
};

const PaperSummaryDashboard: React.FC = () => {
    const [papers, setPapers] = useState(INITIAL_MOCK_PAPERS);
    const [isLoading, setIsLoading] = useState(false);
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

    // Existing useEffect for data fetching
    useEffect(() => {
        const fetchPapers = async () => {
            setIsLoading(true);
            try {
                await new Promise((resolve) => setTimeout(resolve, 1500));

                const updatedPapers = INITIAL_MOCK_PAPERS.map((paper) => ({
                    ...paper,
                    summary: paper.summary + " [Updated]",
                }));

                setPapers(updatedPapers);
                setLastUpdated(new Date());
            } catch (error) {
                console.error("Failed to fetch papers:", error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchPapers();
        const intervalId = setInterval(fetchPapers, 5 * 60 * 1000);
        return () => clearInterval(intervalId);
    }, []);

    // Manual refresh handler
    const handleManualRefresh = () => {
        const fetchPapers = async () => {
            setIsLoading(true);
            try {
                await new Promise((resolve) => setTimeout(resolve, 1500));

                const newPapers = INITIAL_MOCK_PAPERS.map((paper) => ({
                    ...paper,
                    summary: `🆕 ${
                        paper.summary
                    } (Manually Refreshed at ${new Date().toLocaleTimeString()})`,
                }));

                setPapers(newPapers);
                setLastUpdated(new Date());
            } catch (error) {
                console.error("Manual refresh failed:", error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchPapers();
    };

    return (
        <div className="relative min-h-screen overflow-hidden">
            {/* Custom SVG Background */}
            <AnimatedBackground />

            {/* Main Content */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5 }}
                className="relative z-10 container mx-auto p-6 min-h-screen"
            >
                <div className="flex justify-between items-center mb-12">
                    <motion.h1
                        initial={{ y: -50, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        transition={{ type: "spring", stiffness: 100 }}
                        className="text-4xl font-bold text-gray-800"
                    >
                        Daily Research Intelligence
                    </motion.h1>

                    <div className="flex items-center space-x-4">
                        {lastUpdated && (
                            <span className="text-sm text-gray-600">
                                Last Updated: {lastUpdated.toLocaleTimeString()}
                            </span>
                        )}
                        <button
                            onClick={handleManualRefresh}
                            disabled={isLoading}
                            className="p-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 disabled:opacity-50 transition-all"
                        >
                            <RefreshCw
                                size={20}
                                className={isLoading ? "animate-spin" : ""}
                            />
                        </button>
                    </div>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {papers.map((paper, index) => {
                        const DomainIcon: LucideIcon =
                            domainIcons[paper.domain] || BookOpen;

                        return (
                            <motion.div
                                key={paper.id}
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{
                                    delay: index * 0.2,
                                    type: "spring",
                                    stiffness: 100,
                                }}
                                className="relative z-20"
                            >
                                <Card className="h-full flex flex-col bg-white/80 backdrop-blur-sm shadow-lg hover:shadow-2xl transition-all duration-300">
                                    <CardHeader className="flex flex-row items-center space-x-4 border-b pb-3">
                                        <div className="bg-blue-100 p-3 rounded-full">
                                            <DomainIcon
                                                className="text-blue-600"
                                                size={24}
                                            />
                                        </div>
                                        <CardTitle className="text-xl font-semibold text-gray-900">
                                            {paper.title}
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent className="flex-grow flex flex-col justify-between p-6">
                                        <div className="mb-4">
                                            <p className="text-gray-600 mb-4 line-clamp-3">
                                                {paper.summary}
                                            </p>
                                        </div>

                                        <div className="flex justify-between items-center text-gray-500">
                                            <div className="flex items-center space-x-2">
                                                <CalendarDays size={16} />
                                                <span className="text-sm">
                                                    {new Date(
                                                        paper.publishedDate
                                                    ).toLocaleDateString()}
                                                </span>
                                            </div>

                                            <a
                                                href={paper.url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="flex items-center space-x-2 text-blue-600 hover:text-blue-800"
                                            >
                                                <Link2 size={16} />
                                                <span className="text-sm">
                                                    View Paper
                                                </span>
                                            </a>
                                        </div>
                                    </CardContent>
                                </Card>
                            </motion.div>
                        );
                    })}
                </div>
            </motion.div>
        </div>
    );
};

export default PaperSummaryDashboard;
