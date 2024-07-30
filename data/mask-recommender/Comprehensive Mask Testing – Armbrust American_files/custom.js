/** Shopify CDN: Minification failed

Line 57:2 Transforming const to the configured target environment ("es5") is not supported yet
Line 60:2 Transforming const to the configured target environment ("es5") is not supported yet
Line 61:2 Transforming const to the configured target environment ("es5") is not supported yet
Line 74:31 Transforming destructuring to the configured target environment ("es5") is not supported yet
Line 75:2 Transforming let to the configured target environment ("es5") is not supported yet
Line 78:2 Transforming let to the configured target environment ("es5") is not supported yet
Line 79:2 Transforming let to the configured target environment ("es5") is not supported yet
Line 80:2 Transforming let to the configured target environment ("es5") is not supported yet
Line 81:2 Transforming let to the configured target environment ("es5") is not supported yet
Line 82:2 Transforming let to the configured target environment ("es5") is not supported yet
... and 9 more hidden warnings

**/
/**
 * Include your custom JavaScript here.
 *
 * We also offer some hooks so you can plug your own logic. For instance, if you want to be notified when the variant
 * changes on product page, you can attach a listener to the document:
 *
 * document.addEventListener('variant:changed', function(event) {
 *   var variant = event.detail.variant; // Gives you access to the whole variant details
 * });
 *
 * You can also add a listener whenever a product is added to the cart:
 *
 * document.addEventListener('product:added', function(event) {
 *   var variant = event.detail.variant; // Get the variant that was added
 *   var quantity = event.detail.quantity; // Get the quantity that was added
 * });
 *
 * If you just want to force refresh the mini-cart without adding a specific product, you can trigger the event
 * "cart:refresh" in a similar way (in that case, passing the quantity is not necessary):
 *
 * document.documentElement.dispatchEvent(new CustomEvent('cart:refresh', {
 *   bubbles: true
 * }));
 */

/**
 * Function to update the discount ribbon on Nano filter pages
 * @param {string} type Nano air filter template name
 * @param {object} variant Selected variant
 * @returns
 */
function setNanoDiscountPercentage(type, variant) {
  if (
    !type ||
    !variant ||
    !type.includes("nano-air-filter") ||
    !variant.price ||
    !variant.compare_at_price
  )
    return;

  const productMetaPrices = document.querySelector(".ProductMeta__PriceList");
  if (!productMetaPrices) return;

  const percent = 100 - (variant.price / variant.compare_at_price) * 100;
  const innerHTML =
    '<span class="NANO-AirFilterDiscount">' +
    Math.round(percent) +
    "% OFF" +
    "</span>";
  productMetaPrices.innerHTML += innerHTML;
}

/**
 * This function depends of `product_variant_inventory` global variable declared on product-form.liquid
 * @param {object} detail
 * @returns
 */
function sortColorsByInventory({ variant, previousVariant, productData }) {
  let colorSwatchList = document.querySelector(".ColorSwatchList");
  if (!colorSwatchList || !variant || !product_variant_inventory) return;

  let options = {};
  let previusOptions = {};
  let isEqual = true;
  let colorOptionIndex = 0;
  let colorOptionName;

  productData.options.forEach((x, i) => {
    const prop = `option${i + 1}`;
    const op = x.toLowerCase();

    if (op.includes("color")) {
      colorOptionName = prop;
      colorOptionIndex = i;
    } else {
      options[prop] = variant[prop];
      previusOptions[prop] = previousVariant[prop];
      if (isEqual) isEqual = options[prop] === previusOptions[prop];
    }
  });

  if (isEqual || !colorOptionName) return;

  const sorted = productData.variants
    .filter((pd) => {
      const match = Object.entries(options).map(
        ([key]) => pd[key] === variant[key]
      );
      return match.every((x) => x) && pd.available;
    })
    .map((pd) => ({ qty: product_variant_inventory[pd.id], ...pd }))
    .sort((a, b) => b.qty - a.qty);

  let innerHTML = "";

  sorted.forEach((item, index) => {
    const color = item[colorOptionName];
    innerHTML += `
        <li class="HorizontalList__Item" id="colorItem">
          <input id="option-product-template-${colorOptionIndex}-${index}" class="ColorSwatch__Radio" type="radio" name="option-${colorOptionIndex}" value="${color}" data-option-position="${
      colorOptionIndex + 1
    }">
          <label for="option-product-template-${colorOptionIndex}-${index}" class="ColorSwatch ColorSwatch--large ${
      color === "White" ? "ColorSwatch--white" : ""
    }" data-tooltip="${color}" style="background-color: ${color
      .replace(" ", "")
      .toLowerCase()}; ">
            <span class="u-visually-hidden" role="button">${color}</span>
          </label>
        </li>
      `;
  });

  // add fixed black mask for KN95
  const variantName = variant.name.toLowerCase();
  if (variantName.includes("kn95") && variantName.includes("regular")) {
    innerHTML += `
      <li class="HorizontalList__Item" id="colorItem" style="margin-left: 4px;">
        <a href="/products/armbrust-usa-made-black-kn95-style-mask" target="_blank" style="display: block;">
          <label class="ColorSwatch ColorSwatch--large" data-tooltip="Black" style="background-color: #000000;">
            <span class="u-visually-hidden">Black</span>
          </label>
        </a>
      </li>
    `;
  }

  // add elements to color swatch list
  // colorSwatchList.innerHTML = innerHTML;

  // to select the first color available
  // colorSwatchList.children[0].children[0].checked = true;

  // trigger the event to update the selected variant on the product page

  // colorSwatchList.children[0].children[0].dispatchEvent(
    // new Event("change", {
      // bubbles: true,
      // cancelable: true,
      // view: window,
    })
  );

}

document.addEventListener("variant:changed", function (event) {
  if (!event.detail) return;
  setNanoDiscountPercentage(
    event.detail.options.templateSuffix,
    event.detail.variant
  );
  sortColorsByInventory(event.detail);
});

if (window) window.sortColorsByInventory = sortColorsByInventory;
