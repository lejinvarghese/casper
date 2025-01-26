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
    <Card className="bg-white shadow-lg p-4">
        <CardHeader>
            <CardTitle className="text-xl font-semibold">Today</CardTitle>
        </CardHeader>
        <CardContent>
            <div className="text-gray-600">
                <div className="date-card">
                    <p>{new Date().toLocaleDateString()}</p>
                </div>
                <br />
                <div className="weather-card">
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
