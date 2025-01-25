import React from 'react';
import { motion  } from 'framer-motion';
import { BookOpen } from 'lucide-react';

const App: React.FC = () => {
  return (
    <div className="container mx-auto p-6">
      <motion.h1 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-3xl font-bold text-center"
      >
        Research Paper Dashboard
      </motion.h1>
      <div className="flex justify-center mt-4">
        <BookOpen size={48} className="text-blue-500" />
      </div>
    </div>
  );
};

export default App;