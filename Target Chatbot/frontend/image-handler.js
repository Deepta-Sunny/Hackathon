/**
 * Image Handler for File Upload and Processing
 * Handles image selection, validation, preview, and conversion
 */

class ImageHandler {
    constructor(maxFileSize = 5 * 1024 * 1024) { // 5MB default
        this.selectedImages = [];
        this.maxFileSize = maxFileSize;
        this.allowedMimeTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        this.listeners = {
            onImageSelected: [],
            onImageRemoved: [],
            onError: []
        };
    }

    /**
     * Handle file selection from input element
     */
    handleFileSelect(files) {
        const fileArray = Array.from(files);
        Array.forEach.call(fileArray, (file) => {
            this.addImage(file);
        });
    }

    /**
     * Add and validate an image
     */
    addImage(file) {
        // Validate file type
        if (!this.allowedMimeTypes.includes(file.type)) {
            this.emit('onError', `Invalid file type: ${file.type}. Allowed types: JPEG, PNG, GIF, WebP`);
            return;
        }

        // Validate file size
        if (file.size > this.maxFileSize) {
            const maxSizeMB = this.maxFileSize / (1024 * 1024);
            this.emit('onError', `File too large. Maximum size: ${maxSizeMB}MB`);
            return;
        }

        // Create image object
        const imageId = Date.now() + Math.random();
        const reader = new FileReader();

        reader.onload = (event) => {
            const imageData = {
                id: imageId,
                name: file.name,
                type: file.type,
                size: file.size,
                data: event.target.result, // Base64 data URL
                file: file
            };

            this.selectedImages.push(imageData);
            this.emit('onImageSelected', imageData);
        };

        reader.onerror = () => {
            this.emit('onError', 'Error reading file');
        };

        reader.readAsDataURL(file);
    }

    /**
     * Remove image by ID
     */
    removeImage(imageId) {
        this.selectedImages = this.selectedImages.filter(img => img.id !== imageId);
        this.emit('onImageRemoved', imageId);
    }

    /**
     * Get all selected images
     */
    getSelectedImages() {
        return this.selectedImages;
    }

    /**
     * Clear all images
     */
    clearAll() {
        this.selectedImages = [];
    }

    /**
     * Get image count
     */
    getCount() {
        return this.selectedImages.length;
    }

    /**
     * Convert image to specific format
     */
    async convertToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
            reader.readAsDataURL(file);
        });
    }

    /**
     * Validate image dimensions
     */
    async validateDimensions(file, maxWidth = 4096, maxHeight = 4096) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.src = URL.createObjectURL(file);
            img.onload = () => {
                if (img.width <= maxWidth && img.height <= maxHeight) {
                    resolve(true);
                } else {
                    reject(new Error(`Image dimensions (${img.width}x${img.height}) exceed maximum (${maxWidth}x${maxHeight})`));
                }
            };
            img.onerror = () => reject(new Error('Failed to load image'));
        });
    }

    /**
     * Register event listener
     */
    on(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event].push(callback);
        }
    }

    /**
     * Unregister event listener
     */
    off(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
        }
    }

    /**
     * Emit event to all listeners
     */
    emit(event, data = null) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error('Error in listener:', error);
                }
            });
        }
    }
}

// Export for use
export default ImageHandler;
