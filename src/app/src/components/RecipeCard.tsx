import { useState, useEffect } from "react";

// Define the structure of the recipe object
interface Recipe {
    idMeal: string;
    strMeal: string;
    strMealThumb: string;
    strCategory: string;
    strArea: string;
    strInstructions: string;
    strYoutube?: string;
    strSource: string;
    [key: string]: string | undefined;
}

const RecipeCard = () => {
    const [recipe, setRecipe] = useState<Recipe | null>(null);

    useEffect(() => {
        const fetchRecipe = async () => {
            try {
                const response = await fetch(
                    "https://www.themealdb.com/api/json/v1/1/random.php"
                    //Region: www.themealdb.com/api/json/v1/1/filter.php?a=Canadian
                    //Category: www.themealdb.com/api/json/v1/1/filter.php?c=Seafood
                    //Name: www.themealdb.com/api/json/v1/1/search.php?s=Arrabiata
                );
                const data = await response.json();
                setRecipe(data.meals[0]); // Set the first meal from the array
            } catch (error) {
                console.error("Error fetching recipe:", error);
            }
        };

        fetchRecipe();
    }, []);

    if (!recipe) {
        return <p>Loading...</p>;
    }

    // Fix YouTube URL embedding by handling common formats
    const getYouTubeEmbedUrl = (youtubeUrl?: string) => {
        if (!youtubeUrl) return "";
        const videoId = youtubeUrl.split("v=")[1]?.split("&")[0];
        return videoId ? `https://www.youtube.com/embed/${videoId}` : "";
    };

    const getSourceUrl = (sourceUrl: string) => {
        if (sourceUrl && sourceUrl.trim()) {
            const trimmedUrl = sourceUrl.trim();
            if (!trimmedUrl.startsWith("https://")) {
                return `https://${trimmedUrl}`;
            }
            return trimmedUrl;
        }
        return "No source available"; // Fallback if no valid URL
    };

    return (
        <div className="bg-white rounded-lg p-6">
            <h2 className="text-2xl font-bold mb-4">{recipe.strMeal}</h2>
            <img
                src={recipe.strMealThumb}
                alt={recipe.strMeal}
                className="w-full h-64 object-cover mb-4"
            />
            <p className="text-gray-700 mb-4">
                {recipe.strCategory} - {recipe.strArea}
            </p>

            <h3 className="font-semibold mb-2">Ingredients</h3>
            <ul className="list-disc ml-6 mb-4">
                {Array.from({ length: 20 }, (_, i) => i + 1)
                    .filter(
                        (i) =>
                            recipe[`strIngredient${i}`] &&
                            recipe[`strMeasure${i}`]
                    )
                    .map((i) => (
                        <li key={i}>
                            {recipe[`strMeasure${i}`]}{" "}
                            {recipe[`strIngredient${i}`]}
                        </li>
                    ))}
            </ul>

            <h3 className="font-semibold mb-2">Instructions</h3>
            <p className="text-gray-700 mb-4">{recipe.strInstructions}</p>

            {recipe.strYoutube && (
                <div className="mt-4">
                    <h3 className="font-semibold mb-2">Video Tutorial</h3>
                    <iframe
                        width="560"
                        height="315"
                        src={getYouTubeEmbedUrl(recipe.strYoutube)}
                        title="YouTube video player"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                    ></iframe>
                </div>
            )}
            <div className="mt-4">
                <a
                    href={getSourceUrl(recipe.strSource)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:text-blue-700 cursor-pointer z-10"
                >
                    Source
                </a>
            </div>
        </div>
    );
};

export default RecipeCard;
