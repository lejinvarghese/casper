import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "./Card";

interface WeatherCardProps {
    weather: string;
    precipitation: number | null;
    uvIndex: number | null;
    weatherIcon: string;
}

export const WeatherCard: React.FC<WeatherCardProps> = ({
    weather,
    precipitation,
    uvIndex,
    weatherIcon,
}) => (
    <Card className="bg-white/80 backdrop-blur-sm shadow-lg">
        <CardHeader>
            <CardTitle className="text-xl font-semibold">
                <span className="ml-2">
                    {new Date().toLocaleDateString("en-US", {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                    })}
                </span>
            </CardTitle>
        </CardHeader>
        <CardContent>
            <div className="flex flex-col md:flex-row justify-between">
                {/* Left Column: Weather Details */}
                <div className="w-full md:flex-1 md:mr-2">
                    <div className="text-gray-600">
                        <div className="weather-card hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 p-2">
                            <div className="weather-header text-lg font-semibold text-blue-500 mb-2">
                                <p>Weather</p>
                            </div>
                            <div className="weather-details">
                                {weather && <p>Temperature: {weather}</p>}
                                {precipitation !== null && (
                                    <p>Precipitation: {precipitation} in</p>
                                )}
                                {uvIndex !== null && <p>UV Index: {uvIndex}</p>}
                            </div>
                            {weatherIcon && (
                                <img
                                    src={weatherIcon}
                                    alt="Weather icon"
                                    style={{ width: "64px", height: "64px" }}
                                />
                            )}
                        </div>
                    </div>
                </div>

                {/* Right Column: Reminders */}
                <div className="w-full md:flex-1 md:ml-2 mt-4 md:mt-0">
                    <div className="weather-card hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 p-2">
                        <div className="weather-header text-lg font-semibold text-blue-500 mb-2">
                            <p>Reminders</p>
                        </div>
                        <ul className="list-disc pl-5 text-gray-700">
                            <li>9:00 AM - Team meeting</li>
                            <li>12:00 PM - Lunch with client</li>
                            <li>3:00 PM - Project deadline review</li>
                        </ul>
                    </div>
                </div>
            </div>
        </CardContent>
    </Card>
);

export default WeatherCard;
