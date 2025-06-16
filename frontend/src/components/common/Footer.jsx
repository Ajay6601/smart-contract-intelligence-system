import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="max-w-7xl mx-auto py-12 px-4 overflow-hidden sm:px-6 lg:px-8">
        <nav className="-mx-5 -my-2 flex flex-wrap justify-center" aria-label="Footer">
          <div className="px-5 py-2">
            <Link to="/" className="text-base text-gray-500 hover:text-gray-900">
              Home
            </Link>
          </div>

          <div className="px-5 py-2">
            <Link to="/about" className="text-base text-gray-500 hover:text-gray-900">
              About
            </Link>
          </div>

          <div className="px-5 py-2">
            <Link to="/library" className="text-base text-gray-500 hover:text-gray-900">
              Contract Library
            </Link>
          </div>

          <div className="px-5 py-2">
            <Link to="/docs" className="text-base text-gray-500 hover:text-gray-900">
              Documentation
            </Link>
          </div>

          <div className="px-5 py-2">
            <Link to="/pricing" className="text-base text-gray-500 hover:text-gray-900">
              Pricing
            </Link>
          </div>

          <div className="px-5 py-2">
            <Link to="/blog" className="text-base text-gray-500 hover:text-gray-900">
              Blog
            </Link>
          </div>

          <div className="px-5 py-2">
            <Link to="/contact" className="text-base text-gray-500 hover:text-gray-900">
              Contact
            </Link>
          </div>
        </nav>
        <div className="mt-8 flex justify-center space-x-6">
          <a href="#" className="text-gray-400 hover:text-gray-500">
            <span className="sr-only">Twitter</span>
            <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
            </svg>
          </a>

          <a href="#" className="text-gray-400 hover:text-gray-500">
            <span className="sr-only">GitHub</span>
            <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path
                fillRule="evenodd"
                d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                clipRule="evenodd"
              />
            </svg>
          </a>

          <a href="#" className="text-gray-400 hover:text-gray-500">
            <span className="sr-only">Discord</span>
            <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path
                fillRule="evenodd"
                d="M18.93 5.34a16.89 16.89 0 00-4.07-1.25c-.18.33-.39.76-.53 1.11a15.52 15.52 0 00-4.67 0c-.14-.35-.35-.78-.54-1.11-1.4.21-2.8.62-4.07 1.25C2.6 8.88 1.76 12.33 2.15 15.72c1.45 1.06 2.84 1.7 4.22 2.12a14 14 0 001.25-2.05c-.63-.24-1.23-.54-1.8-.89a.08.08 0 01-.02-.12c.12-.09.24-.18.35-.27 2.8 1.29 5.83 1.29 8.62 0 .12.1.24.18.35.27a.08.08 0 01-.02.12c-.57.35-1.17.65-1.8.9.37.7.8 1.4 1.25 2.04 1.38-.42 2.78-1.06 4.22-2.12.46-3.95-.76-7.37-3.34-10.38zM8.31 13.75c-.83 0-1.5-.76-1.5-1.69 0-.92.67-1.69 1.5-1.69s1.5.77 1.5 1.69c0 .93-.67 1.69-1.5 1.69zm5.38 0c-.83 0-1.5-.76-1.5-1.69 0-.92.67-1.69 1.5-1.69s1.5.77 1.5 1.69c0 .93-.67 1.69-1.5 1.69z"
                clipRule="evenodd"
              />
            </svg>
          </a>
        </div>
        <p className="mt-8 text-center text-base text-gray-400">
          &copy; 2025 Smart Contract Intelligence Platform. All rights reserved.
        </p>
      </div>
    </footer>
  );
};

export default Footer;