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

const App: React.FC = () => {
    // State for research papers and weather data
    const [papers, setPapers] = useState(INITIAL_MOCK_PAPERS);
    const [isLoading, setIsLoading] = useState(false);
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
    const [weather, setWeather] = useState<string>("Loading...");
    const [weatherIcon, setWeatherIcon] = useState<string>("");
    const [precipitation, setPrecipitation] = useState<number | null>(null);
    const [uvIndex, setUvIndex] = useState<number | null>(null);

    // State for the active tab: "daily", "research", "nutrition", or "recipes"
    const [activeTab, setActiveTab] = useState<string>("daily");

    // Fetch weather data
    useEffect(() => {
        const fetchWeather = async () => {
            try {
                const apiKey = process.env.REACT_APP_WEATHER_API_KEY;
                const response = await fetch(
                    `http://api.weatherapi.com/v1/current.json?key=${apiKey}&q=Toronto&aqi=no`
                );
                if (!response.ok) {
                    throw new Error("Failed to fetch weather data");
                }
                const data = await response.json();
                const tempCelsius = data.current.temp_c;
                const condition = data.current.condition.text;
                const iconUrl = `https:${data.current.condition.icon}`;
                const feelsLikeCelsius = data.current.feelslike_c;
                const precipInches = data.current.precip_in;
                const uv = data.current.uv;

                setWeather(
                    `${tempCelsius}°C (feels like ${feelsLikeCelsius}°C), ${condition}`
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

    // Fetch research papers (simulate with a delay)
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

    // Manual refresh for research papers
    const handleManualRefresh = () => {
        const fetchPapers = async () => {
            setIsLoading(true);
            try {
                await new Promise((resolve) => setTimeout(resolve, 1500));
                const newPapers = INITIAL_MOCK_PAPERS.map((paper) => ({
                    ...paper,
                    summary: `🆕 ${
                        paper.summary
                    } (Manually refreshed at ${new Date().toLocaleTimeString()})`,
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
                {/* Header */}
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

                {/* Tab Navigation */}
                <div className="flex space-x-4 mb-8 border-b-2">
                    <button
                        onClick={() => setActiveTab("daily")}
                        className={`pb-2 transition-colors ${
                            activeTab === "daily"
                                ? "border-b-4 border-blue-500 text-blue-500"
                                : "text-gray-500 hover:text-gray-700"
                        }`}
                    >
                        Daily Reminders
                    </button>
                    <button
                        onClick={() => setActiveTab("research")}
                        className={`pb-2 transition-colors ${
                            activeTab === "research"
                                ? "border-b-4 border-blue-500 text-blue-500"
                                : "text-gray-500 hover:text-gray-700"
                        }`}
                    >
                        Research Summary
                    </button>
                    <button
                        onClick={() => setActiveTab("nutrition")}
                        className={`pb-2 transition-colors ${
                            activeTab === "nutrition"
                                ? "border-b-4 border-blue-500 text-blue-500"
                                : "text-gray-500 hover:text-gray-700"
                        }`}
                    >
                        Nutrition & Food Guide
                    </button>
                    <button
                        onClick={() => setActiveTab("recipes")}
                        className={`pb-2 transition-colors ${
                            activeTab === "recipes"
                                ? "border-b-4 border-blue-500 text-blue-500"
                                : "text-gray-500 hover:text-gray-700"
                        }`}
                    >
                        Recipes for Food
                    </button>
                </div>

                {/* Tab Content */}
                {activeTab === "daily" && (
                    <div className="space-y-8">
                        {/* Weather and daily reminders */}
                        <WeatherCard
                            weather={weather}
                            precipitation={precipitation}
                            uvIndex={uvIndex}
                            weatherIcon={weatherIcon}
                        />
                        <div className="bg-white shadow-md rounded-lg p-6">
                            <h2 className="text-2xl font-bold mb-4">
                                Today's Reminders
                            </h2>
                            <ul className="list-disc pl-6 text-gray-700">
                                <li>9:00 AM - Team meeting</li>
                                <li>12:00 PM - Lunch with client</li>
                                <li>3:00 PM - Project deadline review</li>
                                <li>Evening - Exercise or a walk</li>
                            </ul>
                            <p className="mt-4 text-sm text-gray-500">
                                Check your calendar for more events and
                                personalized recommendations.
                            </p>
                        </div>
                    </div>
                )}

                {activeTab === "research" && (
                    <div className="space-y-8">
                        <div className="bg-white shadow-md rounded-lg p-6">
                            <h2 className="text-2xl font-bold mb-4">
                                Research Summary
                            </h2>
                            <p className="text-gray-700">
                                Below are the latest research paper summaries
                                updated automatically.
                            </p>
                        </div>
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ duration: 0.5 }}
                            className="grid md:grid-cols-2 lg:grid-cols-3 gap-8"
                        >
                            {papers.map((paper, index) => (
                                <PaperCard
                                    key={paper.id}
                                    paper={paper}
                                    index={index}
                                />
                            ))}
                        </motion.div>
                    </div>
                )}

                {activeTab === "nutrition" && (
                    <div className="bg-white shadow-md rounded-lg p-6">
                        <h2 className="text-2xl font-bold mb-4">
                            Nutrition & Food Guide
                        </h2>
                        <p className="text-gray-700">
                            Nutrition tips, meal planning strategies, and guides
                            to eating healthy will appear here.
                        </p>
                        {/* You can add more detailed components or data later */}
                    </div>
                )}

                {activeTab === "recipes" && (
                    <div className="bg-white shadow-md rounded-lg p-6">
                        <h2 className="text-2xl font-bold mb-4">
                            Recipes for Food
                        </h2>
                        <p className="text-gray-700">
                            Discover delicious recipes tailored to your dietary
                            preferences. More recipes will be added soon.
                        </p>
                        {/* Replace with your recipes components or data */}
                    </div>
                )}
            </motion.div>
        </div>
    );
};

export default App;
