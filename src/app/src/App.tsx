import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { RefreshCw } from "lucide-react";
import { AnimatedBackground } from "./components/AnimatedBackground";
import { WeatherCard } from "./components/WeatherCard";
import { PaperCard } from "./components/PaperCard";
import "./App.css";

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

const PaperSummaryDashboard: React.FC = () => {
    const [papers, setPapers] = useState(INITIAL_MOCK_PAPERS);
    const [isLoading, setIsLoading] = useState(false);
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
    const [weather, setWeather] = useState<string>("Loading...");
    const [weatherIcon, setWeatherIcon] = useState<string>("");
    const [precipitation, setPrecipitation] = useState<number | null>(null);
    const [uvIndex, setUvIndex] = useState<number | null>(null);

    useEffect(() => {
        const fetchWeather = async () => {
            try {
                // Replace with your own OpenWeatherMap API Key, preferably stored in an environment variable
                const response = await fetch(
                    `http://api.weatherapi.com/v1/current.json?key=61efd1207ba144a3abe190905252501&q=Toronto&aqi=no`
                );

                // Check if the response is ok (status code 200-299)
                if (!response.ok) {
                    throw new Error("Failed to fetch weather data");
                }

                const data = await response.json();
                const tempCelsius = data.current.temp_c;
                const condition = data.current.condition.text;
                const iconUrl = `https:${data.current.condition.icon}`; // Prepend 'https:'
                const feelsLikeCelsius = data.current.feelslike_c;
                const precipInches = data.current.precip_in;
                const uv = data.current.uv;

                // Set states with extracted values
                setWeather(
                    `${tempCelsius}°C, (${feelsLikeCelsius}°C), ${condition}`
                );
                setWeatherIcon(iconUrl);
                setPrecipitation(precipInches);
                setUvIndex(uv);
            } catch (error) {
                console.error("Error fetching weather:", error);
                setWeather("Weather data unavailable");
                setWeatherIcon("");
            }
        };

        fetchWeather();
    }, []);

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
            <AnimatedBackground />

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
                        Daily Intelligence
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

                <div className="mb-8">
                    <WeatherCard
                        weather={weather}
                        precipitation={precipitation}
                        uvIndex={uvIndex}
                        weatherIcon={weatherIcon}
                    />
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {papers.map((paper, index) => (
                        <PaperCard key={paper.id} paper={paper} index={index} />
                    ))}
                </div>
            </motion.div>
        </div>
    );
};

export default PaperSummaryDashboard;
