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
    <Card className="bg-white/80 backdrop-blur-sm shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1"> {/* Added hover effects here */}
        <CardHeader>
            <CardTitle className="text-xl font-semibold">Today</CardTitle>
        </CardHeader>
        <CardContent>
            <div className="text-gray-600">
                <div className="date-card hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1"> {/* Added hover effects here */}
                    <p>{new Date().toLocaleDateString()}</p>
                </div>
                <br />
                <div className="weather-card hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1"> {/* Added hover effects here */}
                    <div className="weather-header">
                        <p>Weather</p>
                    </div>
                    <div className="weather-details">
                        {weather !== null && <p>Temperature: {weather}</p>}
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
        </CardContent>
    </Card>
);
