import '@testing-library/jest-dom';

// Mock scrollIntoView
Element.prototype.scrollIntoView = () => {};
