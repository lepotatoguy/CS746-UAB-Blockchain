// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "supportContracts/token/ERC721/ERC721.sol";
import "supportContracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "supportContracts/access/Ownable.sol";
import "supportContracts/utils/Counters.sol";

contract MyNFT is ERC721, ERC721Enumerable, Ownable {
    using Counters for Counters.Counter;
    using Strings for uint256;

    Counters.Counter private _tokenIdCounter;
    mapping(uint256 => string) private _tokenURIs;

    event NFTMinted(address to, uint256 tokenId, string tokenURI);

    constructor(string memory name, string memory symbol) ERC721(name, symbol) {
        // Initialize the counter to start from 1
        _tokenIdCounter.increment();
    }

    function mintNFT(string memory _tokenURI) public onlyOwner {
        require(bytes(_tokenURI).length > 0, "MyNFT: Token URI is empty");

        uint256 newTokenId = _tokenIdCounter.current();
        _safeMint(msg.sender, newTokenId);
        _setTokenURI(newTokenId, _tokenURI);
        _tokenIdCounter.increment();

        emit NFTMinted(msg.sender, newTokenId, _tokenURI);
    }

    function _setTokenURI(uint256 tokenId, string memory _tokenURI) internal {
        require(_exists(tokenId), "MyNFT: URI set of nonexistent token");
        _tokenURIs[tokenId] = _tokenURI;
    }

    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_exists(tokenId), "MyNFT: URI query for nonexistent token");
        return _tokenURIs[tokenId];
    }

    function _beforeTokenTransfer(address from, address to, uint256 tokenId)
        internal
        override(ERC721, ERC721Enumerable)
    {
        super._beforeTokenTransfer(from, to, tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721Enumerable)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
